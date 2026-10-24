#!/usr/bin/env python3
"""Fine-tuning LoRA du modèle de rédaction Mino-IA.

Le dataset contient des paires « prompt + faits déterministes -> compte rendu
JSON ». Le prompt est masqué dans la loss (labels ``-100``) et le padding est
dynamique. Le script fonctionne sur CPU (float32, sans quantification) et sur
GPU (float16 ou 4 bits).

Pour valider le dataset sans dépendance ML :
    python training/finetuning_lora.py --check-dataset
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from api.ml_compat import model_dtype_kwarg  # noqa: E402
from core.dataset import load_pairs, validate_dataset  # noqa: E402
from core.metrics import evaluate_records  # noqa: E402
from core.prompts import format_prompt, is_llama3_model  # noqa: E402

DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
DEFAULT_TRAIN = BASE_DIR / "data" / "dataset_synthetique.csv"
DEFAULT_TEST = BASE_DIR / "data" / "dataset_test.csv"
DEFAULT_OUTPUT = BASE_DIR / "model" / "lora-adapter"


def _eot_token_id(tokenizer) -> int | None:
    """Retourne l'identifiant de ``<|eot_id|>`` s'il existe réellement."""

    token_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")
    unk_token_id = getattr(tokenizer, "unk_token_id", None)
    if isinstance(token_id, int) and token_id >= 0 and token_id != unk_token_id:
        return token_id
    return None


def _target_eos(tokenizer, model_name: str) -> str:
    if is_llama3_model(model_name) and _eot_token_id(tokenizer) is not None:
        return "<|eot_id|>"
    return tokenizer.eos_token or ""


def _eos_token_id(tokenizer, model_name: str) -> int | None:
    if is_llama3_model(model_name):
        token_id = _eot_token_id(tokenizer)
        if token_id is not None:
            return token_id
    return tokenizer.eos_token_id


def tokenize_example(
    prompt: str,
    target: str,
    tokenizer,
    model_name: str,
    max_seq_length: int,
) -> dict[str, list[int]] | None:
    """Tokenise un exemple en masquant le prompt dans les labels."""

    prompt_text = format_prompt(model_name, prompt)
    target_text = target + _target_eos(tokenizer, model_name)
    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    target_ids = tokenizer(target_text, add_special_tokens=False)["input_ids"]
    if not target_ids:
        return None

    max_target = max(1, max_seq_length // 2)
    target_ids = target_ids[:max_target]
    max_prompt = max(1, max_seq_length - len(target_ids))
    if len(prompt_ids) > max_prompt:
        prompt_ids = prompt_ids[-max_prompt:]

    input_ids = prompt_ids + target_ids
    labels = [-100] * len(prompt_ids) + target_ids
    return {
        "input_ids": input_ids,
        "attention_mask": [1] * len(input_ids),
        "labels": labels,
    }


class CausalCollator:
    """Collateur avec padding dynamique et labels ``-100``."""

    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = pad_token_id

    def __call__(self, features: list[dict[str, list[int]]]) -> dict[str, Any]:
        import torch

        max_length = max(len(feature["input_ids"]) for feature in features)
        input_ids = []
        attention_mask = []
        labels = []
        for feature in features:
            padding = max_length - len(feature["input_ids"])
            input_ids.append(feature["input_ids"] + [self.pad_token_id] * padding)
            attention_mask.append(feature["attention_mask"] + [0] * padding)
            labels.append(feature["labels"] + [-100] * padding)
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
        }


def _check_dataset(train_csv: Path, test_csv: Path) -> int:
    exit_code = 0
    for path in (train_csv, test_csv):
        print(f"\nValidation : {path}")
        try:
            report = validate_dataset(path)
        except Exception as exc:
            print(f"  ERREUR : {exc}")
            exit_code = 1
            continue
        print(f"  Valide      : {report['valid']}")
        print(f"  Lignes      : {report['stats']['rows']}")
        print(f"  Évaluations : {report['stats']['evaluations']}")
        print(f"  Statuts     : {report['stats']['status']}")
        print(f"  Probabilités: {report['stats']['probabilities']}")
        if report["errors"]:
            exit_code = 1
            for error in report["errors"][:20]:
                print(f"  - {error}")

    try:
        pairs = load_pairs(train_csv)
        print(f"\nPaires d'entraînement : {len(pairs)}")
        diseases = {}
        for pair in pairs:
            diseases[pair["maladie"]] = diseases.get(pair["maladie"], 0) + 1
        for disease, count in sorted(diseases.items()):
            print(f"  {disease:24s} {count}")
    except Exception as exc:
        print(f"ERREUR de chargement des paires : {exc}")
        exit_code = 1
    return exit_code


def _load_model(args, torch):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    tokenizer.truncation_side = "left"

    cuda = torch.cuda.is_available()
    load_in_4bit = cuda and not args.no_4bit
    kwargs: dict[str, Any] = {"low_cpu_mem_usage": True}
    dtype_kwarg = model_dtype_kwarg()
    if load_in_4bit:
        from transformers import BitsAndBytesConfig

        kwargs["device_map"] = "auto"
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
    elif cuda:
        kwargs["device_map"] = "auto"
        kwargs[dtype_kwarg] = torch.bfloat16 if args.bf16 else torch.float16
    else:
        kwargs[dtype_kwarg] = torch.float32

    model = AutoModelForCausalLM.from_pretrained(args.model, **kwargs)
    if not cuda:
        model.to("cpu")
    if tokenizer.pad_token_id is not None:
        model.config.pad_token_id = tokenizer.pad_token_id
        if getattr(model, "generation_config", None) is not None:
            model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False

    if load_in_4bit:
        from peft import prepare_model_for_kbit_training

        model = prepare_model_for_kbit_training(
            model, use_gradient_checkpointing=args.gradient_checkpointing
        )
    elif args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()

    return model, tokenizer


def _lora_targets(model) -> list[str]:
    candidates = [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ]
    available = {name.split(".")[-1] for name, _ in model.named_modules()}
    targets = [name for name in candidates if name in available]
    if not targets:
        raise RuntimeError(
            "Aucun module LoRA compatible trouvé. Vérifiez l'architecture du modèle."
        )
    return targets


def _evaluate(
    model,
    tokenizer,
    model_name: str,
    pairs: list[dict],
    max_samples: int,
    max_seq_length: int,
    max_new_tokens: int,
    torch,
) -> dict:
    from core.prompts import parse_json_object

    records: list[dict] = []
    model.eval()
    subset = pairs[:max_samples] if max_samples > 0 else pairs
    print(f"  Évaluation sur {len(subset)} paires...")
    with torch.no_grad():
        for index, pair in enumerate(subset, start=1):
            prompt_text = format_prompt(model_name, pair["prompt"])
            inputs = tokenizer(
                prompt_text,
                return_tensors="pt",
                truncation=True,
                max_length=max_seq_length,
            )
            input_length = int(inputs["input_ids"].shape[1])
            inputs = {key: value.to(model.device) for key, value in inputs.items()}
            generated = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=_eos_token_id(tokenizer, model_name),
            )
            text = tokenizer.decode(generated[0][input_length:], skip_special_tokens=True)
            predicted = parse_json_object(text) or {}
            try:
                expected = json.loads(pair["target"])
            except json.JSONDecodeError:
                expected = {}
            records.append({"expected": expected, "predicted": predicted})
            if index % 10 == 0:
                print(f"    {index}/{len(subset)}")

    metrics = evaluate_records(records)
    baseline_records = [
        {
            "expected": record["expected"],
            "predicted": {"probabilite": 0.0, "statut": "sain"},
        }
        for record in records
    ]
    metrics["baseline_zero"] = evaluate_records(baseline_records)
    return metrics


def _print_metrics(metrics: dict) -> None:
    regression = metrics["regression"]
    classification = metrics["classification"]
    print("\n=== Métriques LLM ===")
    print(f"  Paires évaluées : {metrics['n_records']}")
    print(f"  Taux de JSON    : {classification['parse_rate']}")
    print(f"  MAE             : {regression['mae']}")
    print(f"  RMSE            : {regression['rmse']}")
    print(f"  Accuracy        : {classification['accuracy']}")
    print(f"  Sensibilité     : {classification['sensitivity']}")
    print(f"  Spécificité     : {classification['specificity']}")
    print(f"  AUROC           : {classification['auroc']}")
    baseline = metrics.get("baseline_zero", {})
    if baseline:
        print("\n=== Baseline « toujours 0 % » ===")
        print(f"  MAE             : {baseline['regression']['mae']}")
        print(f"  Accuracy        : {baseline['classification']['accuracy']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fine-tuning LoRA Mino-IA")
    parser.add_argument("--model", default=os.environ.get("MINO_MODEL", DEFAULT_MODEL))
    parser.add_argument("--train-csv", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--test-csv", type=Path, default=DEFAULT_TEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation", type=int, default=16)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--warmup-steps", type=int, default=50)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument("--save-steps", type=int, default=500)
    parser.add_argument("--max-train-samples", type=int, default=0)
    parser.add_argument("--max-eval-samples", type=int, default=50)
    parser.add_argument("--gradient-checkpointing", action="store_true")
    parser.add_argument("--no-4bit", action="store_true")
    parser.add_argument("--bf16", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--check-dataset",
        action="store_true",
        help="Valide le dataset et quitte sans charger de modèle",
    )
    args = parser.parse_args(argv)

    if args.check_dataset:
        return _check_dataset(args.train_csv, args.test_csv)

    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig, get_peft_model
        from transformers import Trainer, TrainingArguments
    except ImportError as exc:
        print(f"ERREUR : dépendance ML manquante : {exc}")
        print("Installez avec : pip install -r requirements-ml.txt")
        return 1

    print("Chargement des paires d'entraînement...")
    pairs = load_pairs(args.train_csv)
    if args.max_train_samples > 0:
        pairs = pairs[: args.max_train_samples]
    if not pairs:
        print("ERREUR : aucune paire d'entraînement.")
        return 1
    print(f"  {len(pairs)} paires")

    print(f"Chargement du tokenizer et du modèle : {args.model}")
    started = time.time()
    model, tokenizer = _load_model(args, torch)
    print(f"  Modèle chargé en {time.time() - started:.1f}s")

    print("Tokenisation avec masquage du prompt...")
    tokenized = []
    skipped = 0
    for pair in pairs:
        example = tokenize_example(
            pair["prompt"],
            pair["target"],
            tokenizer,
            args.model,
            args.max_seq_length,
        )
        if example is None:
            skipped += 1
            continue
        tokenized.append(example)
    if not tokenized:
        print("ERREUR : aucune paire tokenisable.")
        return 1
    print(f"  {len(tokenized)} exemples retenus ({skipped} ignorés)")

    dataset = Dataset.from_list(tokenized)
    collator = CausalCollator(tokenizer.pad_token_id)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=_lora_targets(model),
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    cuda = torch.cuda.is_available()
    training_args = TrainingArguments(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_steps=args.warmup_steps,
        weight_decay=0.01,
        logging_steps=args.logging_steps,
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=2,
        fp16=bool(cuda and not args.bf16),
        bf16=bool(cuda and args.bf16),
        optim="adamw_torch",
        report_to="none",
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        gradient_checkpointing=args.gradient_checkpointing,
        max_grad_norm=1.0,
        seed=args.seed,
        data_seed=args.seed,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=collator,
    )

    print("\n=== Entraînement ===")
    print(f"  Modèle            : {args.model}")
    print(f"  Paires            : {len(tokenized)}")
    print(f"  Époques           : {args.epochs}")
    print(f"  Batch effectif    : {args.batch_size * args.gradient_accumulation}")
    print(f"  LR                : {args.lr}")
    print(f"  LoRA r/alpha      : {args.lora_r}/{args.lora_alpha}")
    print(f"  Longueur max      : {args.max_seq_length}")
    print(f"  Device            : {'cuda' if cuda else 'cpu'}")
    print(f"  Sortie            : {args.output_dir}\n")

    result = trainer.train()
    print(f"\nEntraînement terminé. Loss finale : {result.training_loss:.4f}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Adaptateur sauvegardé dans {args.output_dir}")

    metrics: dict[str, Any] = {}
    if args.test_csv.exists():
        try:
            test_pairs = load_pairs(args.test_csv)
            metrics = _evaluate(
                model,
                tokenizer,
                args.model,
                test_pairs,
                args.max_eval_samples,
                args.max_seq_length,
                args.max_new_tokens,
                torch,
            )
            _print_metrics(metrics)
        except Exception as exc:
            print(f"Évaluation impossible : {exc}")
    else:
        print(f"Jeu de test absent : {args.test_csv}")

    metadata = {
        "model": args.model,
        "train_pairs": len(tokenized),
        "epochs": args.epochs,
        "learning_rate": args.lr,
        "batch_size": args.batch_size,
        "gradient_accumulation": args.gradient_accumulation,
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "max_seq_length": args.max_seq_length,
        "seed": args.seed,
        "training_loss": result.training_loss,
        "metrics": metrics,
    }
    (args.output_dir / "training_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

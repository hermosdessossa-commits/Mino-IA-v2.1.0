"""Moteur LLM optionnel, utilisé uniquement pour la rédaction.

Le moteur déterministe reste la source de vérité. Ce module charge un modèle
Hugging Face et un adaptateur LoRA si disponibles, puis reformule un compte
rendu. Toute erreur de chargement ou de génération est non bloquante : l'API
retombe alors sur le compte rendu déterministe.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

from api.ml_compat import model_dtype_kwarg
from core.prompts import format_prompt, parse_json_object

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
DEFAULT_ADAPTER = BASE_DIR / "model" / "lora-adapter"


class LLMEngine:
    """Charge et interroge un LLM de rédaction."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        *,
        enabled: bool = False,
        adapter_dir: str | Path | None = None,
        load_in_4bit: bool = True,
        max_input_tokens: int = 2048,
        max_new_tokens: int = 512,
    ) -> None:
        self.model_name = model_name
        self.enabled = enabled
        self.adapter_dir = Path(adapter_dir) if adapter_dir else DEFAULT_ADAPTER
        self.load_in_4bit = load_in_4bit
        self.max_input_tokens = max_input_tokens
        self.max_new_tokens = max_new_tokens
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self.error: str | None = None
        self._lock = threading.Lock()

    @property
    def loaded(self) -> bool:
        return self.model is not None and self.tokenizer is not None

    @property
    def available(self) -> bool:
        return self.enabled and self.loaded

    def load(self) -> bool:
        """Charge le modèle. Retourne ``True`` en cas de succès."""

        if not self.enabled:
            return False
        if self.loaded:
            return True
        self.error = None
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            self.error = f"Dépendances ML absentes : {exc}"
            LOGGER.warning(self.error)
            return False

        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            LOGGER.info(
                "Chargement du LLM %s (device=%s, 4bit=%s)",
                self.model_name,
                self.device,
                self.load_in_4bit,
            )
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            tokenizer.padding_side = "right"
            tokenizer.truncation_side = "left"

            kwargs: dict[str, Any] = {"low_cpu_mem_usage": True}
            dtype_kwarg = model_dtype_kwarg()
            if self.device == "cuda":
                kwargs["device_map"] = "auto"
                if self.load_in_4bit:
                    from transformers import BitsAndBytesConfig

                    kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                    )
                else:
                    kwargs[dtype_kwarg] = torch.float16
            else:
                kwargs[dtype_kwarg] = torch.float32

            model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
            if self.device == "cpu":
                model.to("cpu")
            if tokenizer.pad_token_id is not None:
                model.config.pad_token_id = tokenizer.pad_token_id
                if getattr(model, "generation_config", None) is not None:
                    model.generation_config.pad_token_id = tokenizer.pad_token_id

            if self.adapter_dir.exists() and (self.adapter_dir / "adapter_config.json").exists():
                try:
                    from peft import PeftModel

                    LOGGER.info("Chargement de l'adaptateur LoRA : %s", self.adapter_dir)
                    model = PeftModel.from_pretrained(model, str(self.adapter_dir))
                    model = model.merge_and_unload()
                except Exception:  # pragma: no cover - dépend du modèle
                    LOGGER.exception("Adaptateur LoRA illisible ; le modèle de base sera utilisé.")

            model.eval()
            self.tokenizer = tokenizer
            self.model = model
            self.device = str(next(model.parameters()).device)
            LOGGER.info("LLM chargé sur %s.", self.device)
            return True
        except Exception as exc:  # pragma: no cover - dépend du matériel
            self.model = None
            self.tokenizer = None
            self.error = f"Échec du chargement du LLM : {exc}"
            LOGGER.exception(self.error)
            return False

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "loaded": self.loaded,
            "model_name": self.model_name,
            "device": self.device,
            "error": self.error,
        }

    def generate_report(self, user_prompt: str) -> dict[str, str] | None:
        """Génère un rapport reformulé, ou ``None`` si la sortie est inutilisable."""

        if not self.available:
            return None
        try:
            import torch
        except ImportError:  # pragma: no cover
            return None

        prompt = format_prompt(self.model_name, user_prompt)
        with self._lock:
            try:
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_input_tokens,
                )
                input_length = int(inputs["input_ids"].shape[1])
                inputs = {key: value.to(self.device) for key, value in inputs.items()}
                with torch.no_grad():
                    generated = self.model.generate(
                        **inputs,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=False,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
                new_tokens = generated[0][input_length:]
                text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            except Exception:  # pragma: no cover - dépend du matériel
                LOGGER.exception("Échec de génération du LLM ; repli déterministe.")
                return None

        parsed = parse_json_object(text)
        if not parsed:
            LOGGER.warning("Sortie LLM non JSON ; repli déterministe.")
            return None
        report = parsed.get("rapport")
        recommendations = parsed.get("recommandations")
        if not isinstance(report, str) or len(report.strip()) < 20:
            LOGGER.warning("Rapport LLM absent ou trop court ; repli déterministe.")
            return None
        if not isinstance(recommendations, str) or len(recommendations.strip()) < 5:
            LOGGER.warning("Recommandations LLM absentes ; repli déterministe.")
            return None
        return {
            "rapport": report.strip()[:8000],
            "recommandations": recommendations.strip()[:4000],
        }

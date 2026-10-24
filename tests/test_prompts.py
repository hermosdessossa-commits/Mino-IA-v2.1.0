"""Tests des prompts et de l'extraction JSON."""

from __future__ import annotations

import json

from core.genetics import predict
from core.prompts import (
    DISCLAIMER,
    build_training_target,
    build_user_prompt,
    format_prompt,
    is_llama3_model,
    parse_json_object,
)


def test_prompt_contains_deterministic_facts():
    prediction = predict("drepanocytose", "A/S", "A/S", "S/S")
    prompt = build_user_prompt(
        "drepanocytose",
        "A/S",
        "A/S",
        "S/S",
        prediction=prediction,
    )
    assert "Drépanocytose" in prompt
    assert "Résultat déterministe" in prompt
    assert "malade" in prompt
    assert "100.0 %" in prompt
    assert "ne pas recalculer" in prompt


def test_prompt_unknown_probability_is_not_zero():
    prediction = predict("drepanocytose", "inconnu", "inconnu", "inconnu")
    prompt = build_user_prompt(
        "drepanocytose", "inconnu", "inconnu", "inconnu", prediction=prediction
    )
    assert "non calculable" in prompt
    assert "0.0 %" not in prompt


def test_training_target_matches_prediction():
    prediction = predict("marfan", "WT", "MUT")
    target = build_training_target(prediction, "Rapport.", "Recommandations.")
    payload = json.loads(target)
    assert payload["probabilite"] == prediction.probability
    assert payload["statut"] == prediction.status
    assert payload["rapport"] == "Rapport."
    assert payload["disclaimer"] == DISCLAIMER


def test_parse_json_object_tolerates_markdown_and_text():
    raw = 'Voici la réponse :\n```json\n{"probabilite": 0.25, "statut": "risque"}\n```\n'
    assert parse_json_object(raw) == {"probabilite": 0.25, "statut": "risque"}
    assert parse_json_object("pas de json") is None
    assert parse_json_object("") is None
    assert parse_json_object("[1, 2, 3]") is None


def test_format_prompt_selects_the_right_chat_template():
    llama3 = format_prompt("meta-llama/Llama-3.1-8B-Instruct", "question")
    assert llama3.startswith("<|begin_of_text|>")
    assert "<|eot_id|>" in llama3

    tiny_llama = format_prompt("TinyLlama/TinyLlama-1.1B-Chat-v1.0", "question")
    assert tiny_llama.startswith("<s>[INST]")
    assert "<|begin_of_text|>" not in tiny_llama

    smollm = format_prompt("HuggingFaceTB/SmolLM2-135M-Instruct", "question")
    assert smollm.startswith("<s>[INST]")

    assert is_llama3_model("meta-llama/Llama-3.2-1B-Instruct")
    assert is_llama3_model("some/llama3-model")
    assert not is_llama3_model("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    assert not is_llama3_model("hf-internal-testing/tiny-random-LlamaForCausalLM")

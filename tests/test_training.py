"""Tests des utilitaires d'entraînement, sans dépendance ML."""

from __future__ import annotations

from training.finetuning_lora import _eos_token_id, _target_eos


class _FakeTokenizer:
    eos_token = "</s>"
    eos_token_id = 2
    unk_token_id = 0

    def convert_tokens_to_ids(self, token: str) -> int:
        return 0 if token == "<|eot_id|>" else 42


def test_llama3_eot_is_ignored_when_the_tokenizer_does_not_know_it():
    tokenizer = _FakeTokenizer()
    assert _target_eos(tokenizer, "TinyLlama/TinyLlama-1.1B-Chat-v1.0") == "</s>"
    assert _eos_token_id(tokenizer, "TinyLlama/TinyLlama-1.1B-Chat-v1.0") == 2


def test_llama3_eot_is_used_when_available():
    class Tokenizer(_FakeTokenizer):
        def convert_tokens_to_ids(self, token: str) -> int:
            return 7 if token == "<|eot_id|>" else 42

    tokenizer = Tokenizer()
    assert _target_eos(tokenizer, "meta-llama/Llama-3.1-8B-Instruct") == "<|eot_id|>"
    assert _eos_token_id(tokenizer, "meta-llama/Llama-3.1-8B-Instruct") == 7

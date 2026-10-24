"""Petites compatibilités entre versions de Transformers.

Transformers 5 a renommé l'argument ``torch_dtype`` en ``dtype``. Le projet
accepte les deux versions sans imposer une version majeure précise.
"""

from __future__ import annotations


def model_dtype_kwarg() -> str:
    """Retourne le nom du paramètre de précision attendu par Transformers."""

    try:
        from transformers import __version__
    except ImportError:
        return "torch_dtype"
    try:
        major = int(__version__.split(".", 1)[0])
    except (AttributeError, ValueError):
        return "torch_dtype"
    return "dtype" if major >= 5 else "torch_dtype"

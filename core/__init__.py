"""Socle métier de Mino-IA.

Le paquet ``core`` ne dépend ni de Flask ni de PyTorch : il contient le registre
des maladies, le moteur mendélien déterministe, la simulation de trios et la
rédaction des comptes rendus. Il peut donc être testé et exécuté seul.
"""

__version__ = "2.1.0"

from core.diseases import DISEASE_IDS, DISEASES, Disease, get_disease, normalize_disease_id
from core.genetics import GenotypeError, Prediction, predict
from core.report import DISCLAIMER, build_recommendations, build_report

__all__ = [
    "DISEASE_IDS",
    "DISEASES",
    "DISCLAIMER",
    "Disease",
    "GenotypeError",
    "Prediction",
    "__version__",
    "build_recommendations",
    "build_report",
    "get_disease",
    "normalize_disease_id",
    "predict",
]

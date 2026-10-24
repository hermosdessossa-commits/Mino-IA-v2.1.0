"""Point d'entrée WSGI pour Gunicorn.

Le chargement du LLM est explicitement demandé ici : il n'a lieu que si
``MINO_USE_LLM=1``. Sans LLM, l'API démarre instantanément avec le moteur
déterministe.
"""

from api.app import create_app

app = create_app({"LOAD_LLM_ON_STARTUP": True})

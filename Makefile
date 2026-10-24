PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
HOST ?= 127.0.0.1
PORT ?= 5000
SAMPLES ?= 5000
SEED ?= 42

.PHONY: help install install-ml install-dev test test-cov lint format check dataset validate run docker-build docker-run clean

help:
	@echo "Cibles disponibles :"
	@echo "  make install      Installe l'API déterministe"
	@echo "  make install-ml   Installe les dépendances LLM (GPU recommandé)"
	@echo "  make install-dev  Installe les outils de test et de lint"
	@echo "  make test         Lance la suite pytest"
	@echo "  make test-cov     Lance pytest avec couverture"
	@echo "  make lint         Vérifie le style avec ruff"
	@echo "  make format       Formate le code avec ruff"
	@echo "  make check        Lint + tests + compilation"
	@echo "  make dataset      Régénère le dataset synthétique (5000/42)"
	@echo "  make validate     Valide les CSV train et test"
	@echo "  make run          Démarre l'API en local"
	@echo "  make clean        Supprime les caches et artefacts"

install:
	$(PIP) install -r requirements-api.txt

install-ml:
	$(PIP) install -r requirements-ml.txt

install-dev:
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest -q

test-cov:
	$(PYTHON) -m pytest --cov=core --cov=api --cov-report=term-missing

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

check: lint
	$(PYTHON) -m pytest -q
	$(PYTHON) -m compileall -q core api scripts training tests wsgi.py

dataset:
	$(PYTHON) scripts/generation_dataset.py --samples $(SAMPLES) --seed $(SEED)

validate:
	$(PYTHON) scripts/validate_dataset.py data/dataset_synthetique.csv data/dataset_test.csv

run:
	$(PYTHON) -m api.app --host $(HOST) --port $(PORT)

docker-build:
	docker build -t mino-ia:2.1.0 .

docker-run:
	docker run --rm -p $(PORT):8000 --env-file .env mino-ia:2.1.0

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete

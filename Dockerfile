FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MINO_ENV=production \
    MINO_HOST=0.0.0.0 \
    MINO_PORT=8000

WORKDIR /app

RUN addgroup --system mino \
    && adduser --system --ingroup mino --home /app mino

COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

COPY core ./core
COPY api ./api
COPY scripts ./scripts
COPY wsgi.py pyproject.toml README.md ./

RUN mkdir -p /app/var /app/model \
    && chown -R mino:mino /app

USER mino

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]

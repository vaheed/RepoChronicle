FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY migrations ./migrations
COPY scripts ./scripts

RUN python -m pip install --upgrade pip \
    && pip install ".[channels,local-embeddings]"

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /var/lib/repochronicle/models /var/lib/repochronicle/workspaces \
    && chown -R appuser:appuser /app /var/lib/repochronicle

USER appuser

EXPOSE 8080 8090

CMD ["uvicorn", "repochronicle.api:app", "--host", "0.0.0.0", "--port", "8080"]

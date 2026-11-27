FROM python:3.12-slim

ARG POETRY_VERSION=2.1.4

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry-cache

WORKDIR /code

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/tmp/poetry-cache \
    poetry install --only main --no-root

COPY . .

RUN useradd --create-home --uid 1000 appuser \
 && mkdir -p /code/media \
 && chown -R appuser:appuser /code/media \
 && chmod +x /code/docker/entrypoint.sh

USER appuser

ENV PYTHONPATH=/code/app

EXPOSE 8000

ENTRYPOINT ["/code/docker/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
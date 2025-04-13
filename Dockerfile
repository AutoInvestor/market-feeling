FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python - && \
    mv $HOME/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-root

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "stock_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

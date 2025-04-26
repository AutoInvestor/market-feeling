FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME=/opt/poetry \
    PATH="/opt/poetry/bin:$PATH" \
    PYTHONPATH="/app/packages"

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl gcc build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-interaction --without dev --no-root

COPY . /app

# Kubernetes will override these with the real secrets via env.
ENV GCP_PROJECT="" \
    PUBSUB_TOPIC="" \
    MONGODB_URI="" \
    MONGODB_DB=""

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "stock_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

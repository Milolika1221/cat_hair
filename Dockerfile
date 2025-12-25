# Stage 1: Builder
FROM python:3.13-slim-bookworm AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libglib2.0-0 \
    libgomp1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .

# Устанавливаем глобально (без .venv)
RUN pip install uv && \
    uv pip install --system --no-cache-dir -e .

# Stage 2: Runtime
FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y \
    libpq5 \
    libgl1 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' appuser
USER appuser

WORKDIR /app

# Копируем системный Python (где всё установлено)
COPY --from=builder --chown=appuser /usr/local /usr/local

COPY --chown=appuser src/ ./src/
COPY --chown=appuser pyproject.toml .

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    TF_CPP_MIN_LOG_LEVEL=2

EXPOSE 8000

CMD ["uvicorn", "cat_server.main:app", "--host", "0.0.0.0", "--port", "8000"]

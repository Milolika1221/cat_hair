# Stage 1: Builder
FROM python:3.13-slim-bookworm AS builder

# Системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libglib2.0-0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем ВСЁ перед установкой
COPY pyproject.toml .
COPY src/ ./src/

# Обычная установка (БЕЗ -e!) → код попадает в site-packages
RUN pip install uv --no-cache-dir && \
    uv pip install --system --no-cache-dir .

# Stage 2: Runtime
FROM python:3.13-slim-bookworm

# Runtime-зависимости
RUN apt-get update && apt-get install -y \
    libpq5 \
    libgl1 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Безопасный пользователь
RUN adduser --disabled-password --gecos '' appuser
USER appuser

WORKDIR /app

# Копируем ТОЛЬКО установленные пакеты (код внутри!)
COPY --from=builder /usr/local /usr/local

# НЕ копируем src/! НЕ копируем pyproject.toml! (они не нужны в runtime)
# ❌ УДАЛИТЕ ЭТИ СТРОКИ:
# COPY --chown=appuser pyproject.toml .
# COPY --chown=appuser ./src/cat_server/alembic.ini .

# Переменные окружения (PYTHONPATH НЕ НУЖЕН!)
ENV PYTHONUNBUFFERED=1 \
    TF_CPP_MIN_LOG_LEVEL=2

EXPOSE 8000

# Запуск через uvicorn
CMD ["uvicorn", "cat_server.main:app", "--host", "0.0.0.0", "--port", "8000"]

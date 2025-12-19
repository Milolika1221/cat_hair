# Stage 1: Builder - для сборки зависимостей
FROM python:3.13-slim-bookworm AS builder

# Устанавливаем системные зависимости
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

# Копируем зависимости
COPY pyproject.toml .

# Устанавливаем uv и зависимости
RUN pip install uv && \
    UV_PROJECT_ENVIRONMENT=/app/.venv uv pip install --system -e .

# Stage 2: Runtime - финальный образ
FROM python:3.13-slim-bookworm

# Устанавливаем runtime зависимости
RUN apt-get update && apt-get install -y \
    libpq5 \
    libgl1 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя без пароля
RUN adduser --disabled-password --gecos '' appuser
USER appuser

WORKDIR /app

# Копируем установленные пакеты
COPY --from=builder --chown=appuser /usr/local /usr/local

# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Копируем ВЕСЬ src/ в корень приложения
COPY --chown=appuser src/ ./src/

# Копируем конфигурационные файлы
COPY --chown=appuser pyproject.toml .
COPY --chown=appuser ./src/cat_server/alembic.ini .

# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Правильный PYTHONPATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV TF_CPP_MIN_LOG_LEVEL=2

# Экспонируем порт
EXPOSE 8000

# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Правильный путь к приложению
CMD ["cat-server"]

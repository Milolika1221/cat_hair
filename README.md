**Приложение** (cat_hair_app) - Мобильное приложение. Готовую сборку (.ark файл) можно скачать в разделе **Releases** этой ветки.

**Сервер** (cat_server_development) - Бэкенд на Python с FastAPI и нейронной сетью для обработки изображений. Сервер необходимо размещать на хосте (платно), либо можно проверить локально, но тогда нужно менять IP

## Ссылка на Docker (только сервер): https://hub.docker.com/r/mila221/cat-hair-api

## Подробная инструкция для сервера (локальный запуск)
## Подготовка проекта
Скачайте код сервера из ветки cat_server_development:
```bash
# git clone -b cat_server_development https://github.com/Milolika1221/cat_hair.git
cd cat_hair
```
## Установка пакетного менеджера UV
```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Или с помощью официальных python-установщиков [PyPI](https://pypi.org/project/uv/):

```bash
# С помощью pip.
pip install uv
```

```bash
# Или pipx.
pipx install uv
```

## Установка пакетов (библиотек)
Команда сначала проверяет установленные пакеты, а потом собирает (или пересобирает) проект.
```bash
# Установка из зависисмостей указанных в конфигурационном файле(pyproject.toml)
uv pip install -e .
```

Сборка проекта
```bash 
# Собирает проект, создаёт архив и пакет, которые можно отправить в официальный репозиторий pip
uv build
```

## Инициализация базы данных
Перед первым запуском необходимо создать и настроить БД:
```bash 
uv run python -m cat_server.scripts.database_init
```

## Запуск сервера и нейронной сети
```bash
# основной сервер
uv run cat-server
```
```bash
# нейронка
uv run cat-neural
```

## Локальная проверка и доступ с других устройств
Для доступа к серверу с телефона или другого компьютера в той же сети:

Вариант A — Через VS Code:
  -Запустите перенаправление порта 8000

Вариант B — Вручную (если устройства в одной Wi-Fi сети):
  1. Найдите локальный IP-адрес компьютера:
     ```bash
        # Windows
        ipconfig
        # macOS/Linux
        ifconfig
     ```
  2. Подключитесь с другого устройства по адресу: http://[ВАШ_IP]:8000 (надо будет изменить для приложения - BASE_URL)

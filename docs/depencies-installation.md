## Установка пакетного менеджера

Стандартные утилиты для установки:

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

## Запуск проекта осуществлять с помощью ***uv***

```bash
# основной сервер
uv run cat-server
```
```bash
# нейронка
uv run cat-neural
```

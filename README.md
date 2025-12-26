# **Мобильное приложение** (ветвь cat_hair_app)
Готовую сборку (.ark файл) можно скачать в разделе **Releases** этой ветки, либо по QR-код ниже.

![qr-code](https://github.com/user-attachments/assets/b27b843c-915c-4db0-8f45-678ce3eed9e2)

## **ВАЖНАЯ ИНФОРМАЦИЯ:** 
Так как сервер не опубликован, то .ark-версия приложения не покажет функционал нейросети. Для этого придется скачать исходный код приложения из ветви и изменить BASE_URL (указать IP вашего локального или развернутого сервера).

## **Docker-образ для работы с приложением:**

**Ссылка на образ:** https://hub.docker.com/r/mila221/cathair-dev

## Быстрое использование:
```bash
# 1. Скачать образ
docker pull mila221/cathair-dev

# 2. Собрать APK 
docker run --rm -v $(pwd):/output mila221/cathair-dev \
  sh -c "./gradlew assembleDebug && cp /opt/project/app/build/outputs/apk/debug/*.apk /output/"

# 3. Изучить код
docker run -it --rm mila221/cathair-dev ls /opt/project/app/src/main/kotlin/
```

## Интерактивная работа с кодом:
Если вам нужно редактировать код, запускать тесты или работать с проектом напрямую:
```bash
# Способ A: Запустить командную оболочку внутри контейнера
docker run -it --rm \
  -v $(pwd)/my_project:/opt/project \
  mila221/cathair-dev \
  /bin/bash

# Теперь вы внутри контейнера и можете:
# cd /opt/project
# nano app/src/main/kotlin/com/example/analys/MainActivity.kt  # Редактировать код
# ./gradlew assembleDebug  # Собрать APK
# ./gradlew test          # Запустить тесты
# find /opt/project -name "*.kt"  # Найти все Kotlin файлы


# Способ B: Создать постоянную среду разработки
docker run -d --name cathair_workspace \
  -v $(pwd)/my_project:/opt/project \
  --restart unless-stopped \
  mila221/cathair-dev \
  sleep infinity

# Подключиться к запущенному контейнеру в любое время
docker exec -it cathair_workspace /bin/bash


# Способ C: Прямой доступ к конкретным файлам
# 1. Просмотреть структуру проекта
docker run --rm mila221/cathair-dev find /opt/project/app/src/main/kotlin/ -type f -name "*.kt"

# 2. Посмотреть конкретный файл
docker run --rm mila221/cathair-dev cat /opt/project/app/src/main/kotlin/com/example/analys/MainActivity.kt

# 3. Изменить BASE_URL и собрать (все в одной команде)
docker run --rm -v $(pwd):/output mila221/cathair-dev \
  sh -c "sed -i 's/BASE_URL = .*/BASE_URL = \"http:\/\/ВАШ_IP:8000\/\"/' /opt/project/app/src/main/kotlin/com/example/analys/MainActivity.kt && ./gradlew assembleDebug && cp /opt/project/app/build/outputs/apk/debug/*.apk /output/"
```

# **Сервер** (ветвь cat_server_development)
Бэкенд на Python с FastAPI и нейронной сетью для обработки изображений. 

Сервер необходимо размещать на хосте (платно), либо можно проверить локально, но тогда нужно менять IP

[**Докер Образ**](https://hub.docker.com/layers/mkken1/cat-hair/stable/images/sha256-dd180076c488970ce9fc1652a0c01c639ccc0f4f9943406b7fd42f7c0d56032e)

## Docker Hub - установка и запуск сервера
## **1. Установка образа**
Скачайте образ сервера с Docker Hub:
```bash
docker pull mkken1/cat-hair
```
## **2. Скачать docker-compose.yml файл** 
Название папки - "для Docker Hub"
## **3. Команда для запуска**
Запустите весь сервер с базой данных одной командой:
```bash
docker-compose up -d
```
## **4. Предварительная настройка
```bash
# Создание таблиц в БД
docker compose exec app db-init

# Добавление стрижек в БД
docker compose exec app add-haircuts

# Запуск нейронной сети (желательно открыть в новом терминале)
docker compose exec app cat-neural

# Контроль логов (опционально)
docker compose logs app
```
## **Проверка работы:**

Сервер: http://localhost:8000

Документация API: http://localhost:8000/docs

Health check: http://localhost:8000/health

# Подробная инструкция для сервера (локальный запуск, если возникли проблемы с докером)
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
Команда сначала проверяет установленные пакеты, а потом собирает (или пересобирает) проект. Всегда применять при изменении проекта.
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
uv run db-init
```

## Добавление стрижек в базу данных 
Создание каталога стрижек
```bash 
uv run add-haircuts
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
















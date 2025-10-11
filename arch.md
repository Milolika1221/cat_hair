# Просто небольшой гид по простенькой архитектуре

cat_haircut/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Точка входа + DI контейнер
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Конфигурация
│   │   └── dependencies.py    # Зависимости
│   ├── domain/                # Ядро системы
│   │   ├── __init__.py
│   │   ├── entities.py        # Все сущности в одном файле
│   │   └── interfaces.py      # Все интерфейсы в одном файле
│   ├── services/              # Бизнес-сервисы (application layer)
│   │   ├── __init__.py
│   │   ├── session_service.py
│   │   ├── image_service.py
│   │   └── recommendation_service.py
│   ├── infrastructure/        # Внешние реализации
│   │   ├── __init__.py
│   │   ├── database.py        # Работа с БД
│   │   ├── repositories.py    # Реализации репозиториев
│   │   └── neural_client.py   # Клиент для ИИ сервиса
│   └── api/
│       ├── __init__.py
│       ├── schemas.py         # Все схемы в одном файле
│       └── endpoints.py       # Все эндпоинты в одном файле
├── requirements.txt
└── README.md
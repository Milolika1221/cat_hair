cat_grooming_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Точка входа
│   ├── api/                    # Эндпоинты
│   │   ├── __init__.py
│   │   ├── dependencies.py     # Зависимости (DI)
│   │   └── endpoints/          # Группы эндпоинтов
│   │       ├── __init__.py
│   │       ├── cats.py
│   │       └── grooming.py
│   ├── core/                   # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py          # Конфигурация
│   │   └── exceptions.py      # Кастомные исключения
│   ├── domain/                # Доменный слой (бизнес-логика)
│   │   ├── __init__.py
│   │   ├── models/            # Бизнес-модели
│   │   ├── services/          # Бизнес-сервисы
│   │   └── interfaces/        # Абстракции (интерфейсы)
│   ├── infrastructure/        # Инфраструктурный слой
│   │   ├── __init__.py
│   │   ├── database/          # Работа с БД
│   │   └── repositories/      # Реализации репозиториев
│   └── presentation/          # Представление (DTO, схемы)
│       ├── __init__.py
│       └── schemas/           # Pydantic схемы
├── tests/
└── requirements.txt
# Сервис объявлений с аутентификацией и управлением пользователями

Сервис для создания, просмотра, обновления, удаления и поиска объявлений о купле-продаже.  
Реализована **аутентификация через JWT** (срок действия токена — 48 часов) и **система ролей** (user, admin) для разграничения прав доступа.

## Функциональность

### Пользователи

- `POST /user/` — создание нового пользователя (доступно всем)
- `GET /user/{user_id}` — получение информации о пользователе по ID (доступно всем)
- `GET /user/` — получение списка всех пользователей (только для администраторов)
- `PATCH /user/{user_id}` — обновление своих данных (для владельца или администратора)
- `DELETE /user/{user_id}` — удаление своего аккаунта (для владельца или администратора)

### Аутентификация

- `POST /login` — получение JWT-токена (в теле: `username` и `password`). Токен действителен 48 часов.

### Объявления

- `POST /advertisement/` — создание объявления (только для авторизованных пользователей)
- `GET /advertisement/{ad_id}` — получение объявления по ID (доступно всем)
- `PATCH /advertisement/{ad_id}` — обновление своего объявления (для автора или администратора)
- `DELETE /advertisement/{ad_id}` — удаление своего объявления (для автора или администратора)
- `GET /advertisement/` — поиск объявлений с фильтрацией (доступно всем)

#### Поля объявления

| Поле         | Тип      | Обязательное | Описание                      |
|--------------|----------|--------------|-------------------------------|
| title        | string   | да           | Заголовок объявления          |
| description  | string   | нет          | Описание                      |
| price        | float    | да           | Цена                          |
| author       | string   | (авто)       | Имя автора (из токена)        |
| created_at   | datetime | авто         | Дата создания                 |

*Примечание:* поле `author` не передаётся при создании — оно автоматически подставляется из данных текущего пользователя (по токену).

#### Поля пользователя

| Поле       | Тип      | Обязательное | Описание                     |
|------------|----------|--------------|------------------------------|
| username   | string   | да           | Уникальное имя пользователя  |
| email      | string   | да           | Уникальный email             |
| password   | string   | да (только при создании) | Пароль (не хранится в открытом виде) |
| role       | string   | авто         | Роль: `user` (по умолчанию) или `admin` |
| created_at | datetime | авто         | Дата регистрации             |

## Права доступа (роли)

| Роль   | Права                                                                                                                                     |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Неавторизован | • Создание пользователя<br>• Просмотр пользователя по ID<br>• Просмотр объявления по ID<br>• Поиск объявлений |
| user   | + все права неавторизованного<br>• Обновление своих данных<br>• Удаление себя<br>• Создание объявления<br>• Обновление своего объявления<br>• Удаление своего объявления |
| admin  | + любые действия с любыми сущностями (полный доступ)                                                                                     |

## Технологии

- Python 3.11
- FastAPI — веб-фреймворк
- SQLAlchemy 2.0 (асинхронный) — ORM
- PostgreSQL — база данных
- Alembic — миграции БД
- Docker / Docker Compose — контейнеризация
- Pydantic v2 — валидация данных
- python-jose[cryptography] — создание и проверка JWT
- passlib[bcrypt] — хеширование паролей

## Запуск проекта

### Локальный запуск (без Docker)

1. Клонируйте репозиторий:
   ```bash
   git clone <url>
   cd fast_api_1
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/Mac
   .venv\Scripts\activate         # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` на основе `.env.example` и отредактируйте параметры:
   ```ini
   POSTGRES_USER=my_user
   POSTGRES_PASSWORD=my_password
   POSTGRES_DB=my_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   SECRET_KEY=your-secret-key-here  # обязательно укажите свой секретный ключ
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_HOURS=48
   ```

5. Убедитесь, что PostgreSQL запущен и база данных существует:
   ```sql
   CREATE USER my_user WITH PASSWORD 'my_password';
   CREATE DATABASE my_db OWNER my_user;
   ```

6. Примените миграции Alembic (создание таблиц и каскадных связей):
   ```bash
   alembic upgrade head
   ```

7. Запустите сервер:
   ```bash
   uvicorn app.app:app --reload
   ```

   Сервер будет доступен по адресу http://127.0.0.1:8000.  
   Документация Swagger — http://127.0.0.1:8000/docs.

### Запуск через Docker

1. Убедитесь, что Docker и Docker Compose установлены.

2. Создайте файл `.env` на основе `.env.example`. Для Docker укажите `POSTGRES_HOST=db`:
   ```ini
   POSTGRES_USER=my_user
   POSTGRES_PASSWORD=my_password
   POSTGRES_DB=my_db
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_HOURS=48
   ```

3. Запустите контейнеры:
   ```bash
   docker-compose up --build
   ```

   Приложение будет доступно по адресу http://localhost:8080.  
   Документация — http://localhost:8080/docs.

## Переменные окружения

| Переменная               | Описание                               | Пример значения    |
|--------------------------|----------------------------------------|--------------------|
| POSTGRES_USER            | Имя пользователя PostgreSQL            | my_user          |
| POSTGRES_PASSWORD        | Пароль пользователя                    | my_password      |
| POSTGRES_DB              | Название базы данных                   | my_db            |
| POSTGRES_HOST            | Хост PostgreSQL                        | localhost / db   |
| POSTGRES_PORT            | Порт PostgreSQL                        | 5432             |
| SECRET_KEY               | Секретный ключ для подписи JWT         | ваш-секрет-ключ  |
| ALGORITHM                | Алгоритм шифрования JWT (рекомендуется HS256) | HS256     |
| ACCESS_TOKEN_EXPIRE_HOURS| Время жизни токена в часах              | 48               |

## Примеры запросов

### 1. Создание пользователя
```bash
curl -X POST "http://localhost:8000/user/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

### 2. Получение токена (логин)
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure123"
  }'
```
Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 3. Создание объявления (требуется токен)
```bash
curl -X POST "http://localhost:8000/advertisement/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ваш_токен>" \
  -d '{
    "title": "Продам велосипед",
    "description": "Спортивный, почти новый",
    "price": 15000.5
  }'
```

### 4. Получение объявления по ID (доступно без токена)
```bash
curl "http://localhost:8000/advertisement/1"
```

### 5. Обновление своего объявления (требуется токен автора или админа)
```bash
curl -X PATCH "http://localhost:8000/advertisement/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ваш_токен>" \
  -d '{"price": 14000}'
```

### 6. Поиск объявлений (доступно без токена)
```bash
curl "http://localhost:8000/advertisement?title=велосипед&price_min=10000&price_max=20000"
```

### 7. Получение списка пользователей (только для администраторов)
```bash
curl -H "Authorization: Bearer <токен_админа>" \
  "http://localhost:8000/user/"
```

## Структура проекта

```
fast_api_1/
├── app/
│   ├── __init__.py
│   ├── app.py                  # основной файл FastAPI
│   ├── auth.py                  # функции хеширования и создания JWT
│   ├── config.py                 # загрузка конфигурации из .env
│   ├── database.py               # настройка SQLAlchemy, engine, Base
│   ├── dependencies.py           # зависимости (получение сессии, текущего пользователя)
│   ├── lifespan.py               # создание таблиц при старте
│   ├── models.py                 # SQLAlchemy модели
│   ├── schemas.py                # Pydantic схемы
│   ├── services.py               # CRUD операции
│   └── routers/                  # маршруты
│       ├── users.py              # эндпоинты для пользователей
│       └── advertisements.py     # эндпоинты для объявлений
├── alembic/                      # миграции Alembic
│   ├── versions/
│   ├── env.py
│   └── ...
├── .env.example                   # пример переменных окружения
├── .gitignore
├── alembic.ini                    # конфигурация Alembic
├── docker-compose.yml             # запуск приложения и PostgreSQL
├── Dockerfile
└── requirements.txt               # зависимости Python
```

## Примечания

- При первом запуске таблицы в базе данных создаются автоматически (через `lifespan`), но для обновления схемы (например, добавления внешних ключей с `ondelete`) рекомендуется использовать **Alembic**. В проекте уже настроены миграции.
- При удалении пользователя все его объявления удаляются каскадно (благодаря `ondelete="CASCADE"` в модели).
- Пароли хранятся в захешированном виде (bcrypt).
- Токен следует передавать в заголовке `Authorization: Bearer <token>`.
- Роль администратора можно назначить только напрямую в базе данных (или через миграцию), через API это не предусмотрено.

## Скриншот документации
<img width="1857" height="1873" alt="2026-03-11_12-42-07" src="https://github.com/user-attachments/assets/b0886bb5-6956-45d7-a046-d1954929c0cc" />


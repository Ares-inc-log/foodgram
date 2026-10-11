# Foodgram — продуктовый помощник

Foodgram — сайт для публикации рецептов. Пользователи могут создавать рецепты, подписываться на авторов, добавлять рецепты в избранное и в список покупок, а затем скачивать сводный список ингредиентов для похода в магазин.

## Возможности

- Регистрация и авторизация пользователей.
- Создание, редактирование и удаление собственных рецептов (с изображением, ингредиентами, тегами и временем приготовления).
- Фильтрация рецептов по тегам (комбинация «или»), по автору, по избранному и по списку покупок.
- Избранное: добавление и удаление рецептов (только для авторизованных).
- Подписки на авторов.
- Список покупок: добавление рецептов и скачивание `.txt`-файла, в котором одинаковые ингредиенты суммируются.
- Короткая ссылка на рецепт, не меняющаяся после редактирования.
- Документация API доступна по адресу `/api/docs/`.

## Технологии

- Python 3.12, Django 6.1, Django REST Framework
- django-filter, Djoser
- PostgreSQL 15
- Gunicorn, Nginx
- React (фронтенд)
- Docker, Docker Compose
- GitHub Actions (CI/CD), Docker Hub
- Ruff (линтер)

## Структура проекта

```
.
├── backend/                       # Django-проект
│   ├── Dockerfile
│   ├── requirements.txt
│   └── foodgram/                  # manage.py, настройки, приложения
├── frontend/                      # React-приложение
├── infra/
│   └── nginx.conf                 # конфиг Nginx
├── docs/                          # документация API (redoc/openapi)
├── docker-compose.yml             # локальный запуск (сборка из исходников)
├── docker-compose.production.yml  # запуск на сервере (готовые образы)
├── ruff.toml
└── .github/workflows/main.yml     # CI/CD
```

## Переменные окружения

Создайте файл `.env` (в репозиторий он не попадает) и заполните его по образцу. Имена переменных должны совпадать с теми, что читает `settings.py`:

```env
POSTGRES_USER=django_user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=django_db
DB_HOST=postgres
DB_PORT=5432

SECRET_KEY=change_me_secret_key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
```

## Локальный запуск

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/Ares-inc-log/foodgram.git
   cd foodgram
   ```

2. Создайте файл `.env` (см. раздел выше).

3. Соберите и запустите контейнеры:

   ```bash
   docker compose up -d --build
   ```

4. Примените миграции, соберите статику и создайте суперпользователя:

   ```bash
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic --no-input
   docker compose exec backend python manage.py createsuperuser
   ```

5. Откройте сайт: <http://127.0.0.1>. Админка: <http://127.0.0.1/admin/>, документация API: <http://127.0.0.1/api/docs/>.

Теги и ингредиенты добавляет администратор через админ-панель.

## Основные эндпоинты API

| Метод | Адрес | Описание |
|---|---|---|
| GET | `/api/recipes/` | Список рецептов (фильтры: `tags`, `author`, `is_favorited`, `is_in_shopping_cart`) |
| POST | `/api/recipes/` | Создать рецепт |
| GET | `/api/recipes/{id}/get-link/` | Короткая ссылка на рецепт |
| POST / DELETE | `/api/recipes/{id}/favorite/` | Добавить в избранное / удалить |
| POST / DELETE | `/api/recipes/{id}/shopping_cart/` | Добавить в список покупок / удалить |
| GET | `/api/recipes/download_shopping_cart/` | Скачать список покупок |
| GET | `/s/{id}/` | Переход по короткой ссылке |

Полное описание запросов и ответов смотрите в `/api/docs/`.

## CI/CD

При каждом push и pull request в ветку `main` запускается workflow `.github/workflows/main.yml`:

1. **lint**: проверка кода backend линтером Ruff.
2. **build_and_push**: сборка образов backend и frontend и отправка на Docker Hub (только при push в `main`).
3. **deploy**: копирование конфигов на сервер, создание `.env`, обновление контейнеров, миграции и сбор статики.
4. **send_message**: уведомление об успешном деплое в Telegram.

### Секреты GitHub Actions

Добавьте в Settings → Secrets and variables → Actions:

| Секрет | Назначение |
|---|---|
| `DOCKER_USERNAME` | Логин Docker Hub |
| `DOCKER_PASSWORD` | Токен доступа Docker Hub с правами Read & Write |
| `HOST` | IP-адрес сервера |
| `USER` | Пользователь на сервере |
| `SSH_KEY` | Приватный SSH-ключ |
| `SSH_PASSPHRASE` | Пароль от ключа (если есть) |
| `ENV_FILE` | Содержимое `.env` для сервера целиком |
| `TELEGRAM_TO` | ID чата для уведомлений |
| `TELEGRAM_TOKEN` | Токен Telegram-бота |

### Подготовка сервера

На сервере должен быть установлен Docker с плагином Compose. Остальное (compose-файл, конфиг Nginx, документация, `.env`) приедет из CI в папку `~/foodgram`.

## Линтер

```bash
pip install ruff
ruff check backend/
```

## Автор

Имя автора: [Hazore](https://github.com/Ares-inc-log)
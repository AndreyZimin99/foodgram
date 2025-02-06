![example workflow](https://github.com/AndreyZimin99/foodgram/actions/workflows/main.yml/badge.svg)

#  Foodgram
   В данном проекте я реализовал работу с API, настройку баз данных и аутентификацию пользователей. Также составил dockerfile для бэкэнда
   - адрес: https://fgm.hopto.org (в данный момент не активен)

**Foodgram** — это платформа, на которой пользователи могут делится своими рецептами, добавлять их в избранное и отслеживать интересных авторов.

## Используемый стек:
   - Django;
   - JavaScript;
   - PostgreSQL;
   - Docker;
   - Gunicorn;
   - Nginx

## Установка

Чтобы развернуть проект на локальной машине, выполните следующие шаги:

1. **Клонируйте репозиторий:**
   ```
   git clone https://github.com/AndreyZimin99/foodgram.git
   cd foodgram
   ```

2. **Запустите проект:**
   ```
   docker compose -f docker-compose.production.yml up -d
   ```
3. **Выполните миграции и соберите статические файлы:**
   ```
   sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
   ```
   ```
   sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
   ```
   ```
   sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
   ```
## Заполнение файла .env
   ```
   POSTGRES_DB=django
   POSTGRES_USER=django
   POSTGRES_PASSWORD=django
   DB_HOST=database
   DB_PORT=5432

   SECRET_KEY = some_secret_key
   DEBUG = True
   ALLOWED_HOSTS = localhost

   DB_ENGINE = django.db.backends.sqlite3
   ```
   
@@@AndreyZimin99@@@

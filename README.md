# Foodgram 

## О проекте

Проект представляет собой онлайн-платформу для публикации кулинарных рецептов, где пользователи могут делиться своими блюдами,
подписываться на любимых авторов и формировать список продуктов для похода в магазин.

Ключевая особенность — возможность создавать **список покупок**. Перед походом в магазин пользователь может скачать сводный файл (TXT) со всеми необходимыми продуктами для выбранных блюд, где ингредиенты суммируются (например, если в двух рецептах нужны яйца, в списке будет общая сумма).

### Стек технологий

Основные инструменты и библиотеки, использованные в разработке:

* [![Python][Python-shield]][Python-url]
* [![Django][Django-shield]][Django-url]
* [![DRF][DRF-shield]][DRF-url]
* [![Docker][Docker-shield]][Docker-url]
* [![Nginx][Nginx-shield]][Nginx-url]
* [![PostgreSQL][Postgres-shield]][Postgres-url]

## Инструкция по развертыванию

### Предварительно

Для работы проекта вам понадобятся установленные:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone git@github.com:ВашНик/foodgram-project-react.git
    cd foodgram-project-react
    ```

2.  **Настройте окружение:**
    В папке `infra/` создайте файл `.env` с переменными:
    ```bash
    POSTGRES_DB=foodgram
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY='вставьте_сюда_ваш_секретный_ключ_django'
    DEBUG=False
    ALLOWED_HOSTS=localhost, 127.0.0.1, backend
    ```

3.  **Запустите контейнеры:**
    ```bash
    cd infra/
    docker compose up -d --build
    ```

4.  **Подготовьте базу данных:**
    Выполните миграции и загрузку справочника ингредиентов:
    ```bash
    docker compose exec backend python manage.py migrate
    docker compose exec backend python manage.py load_ingredients
    docker compose exec backend python manage.py collectstatic --no-input
    ```

5.  **Создайте администратора:**
    ```bash
    docker compose exec backend python manage.py createsuperuser
    ```

### Наполнение базы данных

В проекте реализован специальный скрипт для автоматического наполнения базы данных ингредиентами. Это избавляет от необходимости вводить тысячи продуктов вручную.

Скрипт считывает данные из файла data/ingredients.json и сохраняет их в PostgreSQL.

Как запустить:
```bash
docker compose exec backend python manage.py load_ingredients
```

При успешном выполнении вы увидите сообщение в терминале о количестве добавленных записей.


После развертывания проект доступен по адресу: [http://localhost/](http://localhost/)

---

## Документация
Спецификация API доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)

### Примеры запросов к API

### 1. Получение токена 
**POST** `/api/auth/token/login/`
```json
{
    "email": "user@example.com",
    "password": "strong_password"
}
```
**Ответ:**
```json
{
    "auth_token": "d980345100c529a8f273063f4521405106525732"
}
```

### 2. Создание рецепта (требуется токен)
**POST** `/api/recipes/` 
```json
{
  "ingredients": [
    {"id": 1123, "amount": 10},
    {"id": 15, "amount": 200}
  ],
  "tags": [1, 2],
  "name": "Куриный суп",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
  "text": "Нарезать мясо, варить, добавить овощи.",
  "cooking_time": 45
}
```

### 3. Список покупок
**GET** `/api/recipes/download_shopping_cart/`
**Result:** Текстовый файл shopping-list.txt со списком покупок

### 4. Подписка на автора (требуется токен)
**POST** `/api/users/{id}/subscribe/` 

**Ответ:**
```json
{
    "email": "author@example.com",
    "id": 1,
    "username": "author",
    "first_name": "Иван",
    "last_name": "Иванов",
    "is_subscribed": true,
    "recipes": [],
    "recipes_count": 0
}
```

---

## GitHub Actions (CI/CD)

В репозитории настроен файл (`.github/workflows/main.yml`), который обеспечивает непрерывную интеграцию и доставку.

При пуше в ветку `main` выполняются следующие шаги:

1. Tests: Проверка кода на соответствие стандартам PEP8 (flake8).
2. Build & Push: Сборка Docker-образов для бэкенда и фронтенда и их отправка в Docker Hub.

---

### Контакты
- GitHub: [@melanch-olyy](https://github.com/melanch-olyy)
- Email: olga.samsonova.05@mail.ru

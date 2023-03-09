# __Foodgram project (v1)__
## _Описание_

Foodgram - это продуктовый помощник, позволяющий создавать рецепты и собирать свою коллекцию кулинарных изюминок, подписываясь на других авторов.

#### _Технологии_

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/4?color=green&label=python&logoColor=grey)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

#### _Запуск проекта в dev-режиме_

- Установите и активируйте виртуальное окружение
```
py3.7 -m venv venv
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- Создайте и выполните миграции
```
python manage.py makemigrations
```
```
python manage.py migrate
```
- В папке с файлом manage.py выполните команду для заполнения базы данных тестовыми данными:
```
python manage.py csv_command
```
- создайте пользователя с правами администратора:
```
python manage.py createsuperuser
```
- а затем запустите проект:
```
python3 manage.py runserver
```

#### _Алгоритм регистрации пользователей_
1. Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email, username, first_name, last_name и password на эндпоинт /api/v1/users/.
2. Пользователь отправляет POST-запрос с параметрами email и password на эндпоинт /api/v1/auth/token/login/, в ответе на запрос ему приходит auth-token.
4. При желании пользователь отправляет POST-запрос на эндпоинт /api/v1/users/set_password/ для изменения пароля.

- С примером запроса на регистрацию пользователя можно ознакомиться в [документации](http://localhost/api/docs/redoc.html)

#### _Примеры запросов к API для неавторизованных пользователей_
Неавторизованные пользователи могут просматривать главную страницу с рецептами,  а также страницы отдельных рецептов.
- Пример запроса на получения информации о произведении по id:
```
GET api/v1/recipes/{recipe_id}/
```
- Ответ:
```
{
    "id": 0,
    "tags": [
        {"id": 0,
        ...
        }
    ],
    "author": [
        {
            "id": 0, 
            "name": "string"
            ...
        }
    ]
    "name": "string",
    "text": "test_text",
    "is_favorited": "boolean",
    "is_in_shopping_cart": "boolean",
    "ingredients": [
        {
            "id": 0,
            "name": "string",
            ...
        }
    "cooking_time": "string",
    "image": "string <url>"
}
```

#### _Примеры запросов к API для авторизованных пользователей_
Авторизованные пользователи наделены правом создания, изменения и удаления рецептов, авторами которых они являются, могут подписываться и отписываться от других пользователей, добавлять рецепты в избранное и получать список покупок из рецептов "в корзине".
- Для авторизации зарегистрированному пользователю, необходимо получить токен с помощью следующего запроса
```
POST api/v1/auth/token/login/
```
```
body:
{
    "email": "Test_User@test.com",
    "password": "string"
}
```

"access" - поле, содержащее токен.

- Подписка на автора оформляется следующим запросом:
```
POST api/v1/users/{user_id}/subscribe/
```
- и вернет следующий ответ:
```
{
    "Подписка успешно создана": {
        "email": "string",
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "is_subscribed": boolean,
        "recipes": [{...}],
        "recipes_count": 0
    }
}
```
- С примерами других запросов можно ознакомиться в [документации](http://localhost/api/docs/redoc.html)
- Подробнее про установку DRF можно почитать [здесь](https://github.com/encode/django-rest-framework/blob/master/README.md )

## _Лицензия_

MIT

## _Разработчики_
[Левина Юля](https://github.com/JulLevina)

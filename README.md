# __Foodgram project (v1)__
![API_yamdb workflow](https://github.com/JulLevina/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## _Описание_

Foodgram - это продуктовый помощник, позволяющий создавать рецепты и собирать свою коллекцию кулинарных изюминок, подписываясь на других авторов.

#### _Технологии_

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/4?color=green&label=python&logoColor=grey)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

#### _Запуск проекта в dev-режиме_

- Клонируйте репозиторий с GitHub:
```
git clone https://github.com/JulLevina/yamdb_final.git
```
- подключитесь к удаленному серверу
- установите на сервере [Docker](https://docs.docker.com/engine/install/) и [docker-compose](https://docs.docker.com/compose/install/)
- Запустите проект через docker-compose:
```
sudo docker-compose up
```
- Выполните миграции и заполните базу данных тестовыми данными:
```
sudo docker-compose exec web python manage.py migrate
```
```
sudo docker-compose exec web python manage.py loaddata fixtures.json
```
- Создайте суперпользователя:
```
sudo docker-compose exec web python manage.py createsuperuser
```
- Соберите статику:
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```

#### _Проект доступен по адресу:_

http://jullevina.ddns.net/foodgram/

#### _Примеры запросов к API

- С примерами запросов можно ознакомиться в [документации](http://localhost/api/docs/redoc.html)
- Подробнее про установку DRF можно почитать [здесь](https://github.com/encode/django-rest-framework/blob/master/README.md )

## _Лицензия_

MIT

## _Разработчики_
[Левина Юля](https://github.com/JulLevina)

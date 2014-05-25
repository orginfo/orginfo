http://djbook.ru/rel1.6/
=======

#Создаём своё первое приложение с Django, часть 1
Создание проекта:
`django-admin.py startproject mysite`
Сервер для разработки:
`python manage.py runserver 0.0.0.0:8000`

Команда syncdb анализирует значение INSTALLED_APPS и создает все необходимые таблицы в базе данных, используя настройки базы данных из файла mysite/settings.py. Команда syncdb выполняет все запросы из команды sqlall.
`python manage.py syncdb`

Приложение – это Web-приложение, которое предоставляет определенный функционал – например, Web-блог, хранилище каких-то записей или простое приложение для голосования. Проект – это совокупность приложений и конфигурации сайта. Проект может содержать несколько приложений. Приложение может использоваться несколькими проектами.

Создать приложение:
`python manage.py startapp polls`

Django подставляет в переменную окружения DJANGO_SETTINGS_MODULE значение 'mysite.settings'
`>>> os.getenv('DJANGO_SETTINGS_MODULE')`

Полезные ссылки:
[Развёртывание с WSGI](http://djbook.ru/rel1.6/howto/deployment/wsgi/index.html)

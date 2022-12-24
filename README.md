# todolist (service for notes)
## python 3.10, Django 4.1.4, PostgreSQL

### Для запуска проекта установить зависимости:
    pip install -r requirements.txt
### Установить базу данных PostgreSQL:
    docker run --name name_project -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres
### Заполнить файл .env согласно примеру .env(example)
### Выполнить миграции:
    python manage.py migrate
### Запустить проект
    python manage.py runserver



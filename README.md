CRMLite

Приложение для управления компаниями с использованием Django REST Framework.

Technologies:

- Python
- Poetry
- Django
- Django REST Framework
- Django REST Framework Simple JWT
- SQLite
- drf-spectacular (Swagger / OpenAPI)
_______________________________________________________

Project Setup:

1. Clone the repository:

2. Install dependencies:
  poetry install

3. Apply database migrations:
  poetry run python manage.py migrate

4. Create a superuser:
  poetry run python manage.py createsuperuser

5. Run server:
  poetry run python manage.py runserver

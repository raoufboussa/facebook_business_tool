release: python manage.py migrate --noinput
web: gunicorn connect_api.wsgi --timeout 60
web: python manage.py migrate;gunicorn -b 0.0.0.0:\$PORT -w 3 --env DJANGO_SETTINGS_MODULE=flockProj2.settings flockProj2.wsgi


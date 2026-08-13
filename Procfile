web: gunicorn ai_employee.wsgi:application --bind 0.0.0.0:$PORT --workers 1  --threads 4 --timeout 300 --keepalive 2 --env DJANGO_SETTINGS_MODULE=ai_employee.settings


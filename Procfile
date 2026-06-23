web: gunicorn --chdir backend privai_django.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 300 --max-requests 1

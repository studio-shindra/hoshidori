web: gunicorn config.wsgi
release: python3 manage.py migrate --noinput && python3 manage.py collectstatic --noinput

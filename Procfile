release: python manage.py migrate
# Set worker timeout to 10s (default 30s)
web: gunicorn nourish.wsgi --timeout 10 --log-file -

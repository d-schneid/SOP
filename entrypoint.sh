#!/bin/bash

cd /app/webserver/src/main/sop || exit
python3.9 manage.py migrate --no-input
python3.9 manage.py collectstatic --no-input
python3.9 manage.py createsuperuser --no-input

# Launch memcached for worker syncronization
memcached -d -u root

gunicorn sop.wsgi:application --bind 0.0.0.0:8000 --workers=2 --threads=4

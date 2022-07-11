#!/bin/bash

cd /app/webserver/src/main/sop || exit
python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input
python3 manage.py createsuperuser --no-input

gunicorn sop.wsgi:application --bind 0.0.0.0:8000
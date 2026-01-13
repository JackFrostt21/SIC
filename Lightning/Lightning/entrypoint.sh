#!/bin/bash
python $APP_HOME/manage.py makemigrations
python $APP_HOME/manage.py migrate --noinput
python manage.py collectstatic --noinput

python $APP_HOME/manage.py bot & python $APP_HOME/manage.py runserver 0.0.0.0:8080

exec "$@"
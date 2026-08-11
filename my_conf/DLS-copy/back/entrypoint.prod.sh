#!/bin/bash
set -e

MODE="${RUN_MODE:-app}"

if [ "$MODE" = "app" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  exec gunicorn app.wsgi:application --bind 0.0.0.0:8080 --workers "${GUNICORN_WORKERS:-3}"
elif [ "$MODE" = "bot" ]; then
  exec python manage.py bot
elif [ "$MODE" = "scheduler" ]; then
  exec python manage.py scheduler
else
  exec "$@"
fi

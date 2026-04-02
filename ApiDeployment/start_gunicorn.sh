#!/bin/sh

cd /opt/weatherradar/weatherradar
. /opt/weatherradar/venv/bin/activate
. /opt/weatherradar/venv/bin/postactivate

exec gunicorn -w $GUNICORN_WORKERS "API.weatherradar:create_app()"
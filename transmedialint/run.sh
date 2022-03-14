#!/bin/bash
/transmedialint/deploy_all.sh &
scrapyd &
while ! host $DB_HOST
do
    echo waiting for postgres...
    sleep 1
done
python manage.py runserver 0.0.0.0:8000


#!/bin/bash
/transmedialint/deploy_all.sh &
scrapyd &
python manage.py runserver 0.0.0.0:8000


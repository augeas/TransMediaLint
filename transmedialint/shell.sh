#!/bin/bash
/transmedialint/deploy_all.sh &
scrapyd &
python manage.py shell


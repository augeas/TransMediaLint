

import os
import sys

import django

sys.path.append(os.path.abspath('../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transmedialint.settings')
django.setup()

from scrapers.base_settings import *


BOT_NAME = 'the_spectator'

SPIDER_MODULES = ['the_spectator.spiders']
NEWSPIDER_MODULE = 'the_spectator.spiders'

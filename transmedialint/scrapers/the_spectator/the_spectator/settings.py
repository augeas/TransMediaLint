

import os
from shutil import which
import sys

import django

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
SELENIUM_DRIVER_ARGUMENTS = ['--disable-extensions', '--disable-gpu',
    '--no-sandbox', '--headless']

sys.path.append(os.path.abspath('../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transmedialint.settings')
django.setup()

from scrapers.base_settings import *


BOT_NAME = 'the_spectator'

SPIDER_MODULES = ['the_spectator.spiders']
NEWSPIDER_MODULE = 'the_spectator.spiders'

DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}

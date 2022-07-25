# -*- coding: utf-8 -*-

import os
from shutil import which
import sys

import django

# Scrapy settings for the_times project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
SELENIUM_DRIVER_ARGUMENTS = ['--disable-extensions', '--disable-gpu',
    '--no-sandbox', '--headless']


sys.path.append(os.path.abspath('../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transmedialint.settings')
django.setup()

from scrapers.base_settings import *

#LOG_LEVEL = 'DEBUG'

BOT_NAME = 'the_times'

SPIDER_MODULES = ['the_times.spiders']
NEWSPIDER_MODULE = 'the_times.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'the_times (+http://www.yourdomain.com)'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}





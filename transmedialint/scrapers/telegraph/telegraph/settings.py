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

sys.path.append(os.path.abspath('../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transmedialint.settings')
django.setup()

from scrapers.base_settings import *

LOG_LEVEL = 'INFO'

BOT_NAME = 'telegraph'

SPIDER_MODULES = ['telegraph.spiders']
NEWSPIDER_MODULE = 'telegraph.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'the_times (+http://www.yourdomain.com)'

USER_AGENT =  None

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"


# -*- coding: utf-8 -*-

import os
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

#LOG_LEVEL = 'DEBUG'

BOT_NAME = 'the_times'

SPIDER_MODULES = ['the_times.spiders']
NEWSPIDER_MODULE = 'the_times.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'the_times (+http://www.yourdomain.com)'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}


SPLASH_URL = 'http://{}:8050/'.format(os.environ.get('SPLASH_HOST', 'localhost'))


DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'



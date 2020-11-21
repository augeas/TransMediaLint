

from datetime import datetime
import itertools
import os
import re

from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify
import pytz
from scrapyd_api import ScrapydAPI

from sources.models import Article, Author, Source
from transmedialint import settings

class Crawler(object):

    solr_url = 'http://{}:8983/solr/articles/update/extract'.format(
        os.environ.get('SOLR_HOST', 'localhost'))
    
    @classmethod
    def get_slug(cls):
        return slugify(cls.title)


    @classmethod
    def date_last_scraped(cls):
        try:
            return Article.objects.filter(source=cls.get_object()).order_by(
                '-date_retrieved').first().date_retrieved
        except:
            return datetime.fromtimestamp(0)

        
    @classmethod
    def scrape(cls, terms=settings.DEFAULT_TERMS):
        scrapyd = ScrapydAPI('http://{}:6800'.format(os.environ.get(
            'SCRAPING_HOST', 'localhost')))
        scrapyd.schedule(cls.crawler, 'search', query=' '.join(terms),
            last_scraped=cls.date_last_scraped().isoformat())

        
    @classmethod
    def get_object(cls):
        region, city = cls.timezone.zone.split('/')
        source, created = Source.objects.get_or_create(name=cls.__name__,
            title=cls.title,
            slug=cls.get_slug(),
            region=region,
            city=city)
        if created:
            source.save()
        return source

        
class TheSun(Crawler):

    timezone = pytz.timezone('Europe/London')
    title = 'The Sun'
    crawler = 'the_sun'
            
class TheDailyMail(Crawler):

    timezone = pytz.timezone('Europe/London')
    title = 'The Daily Mail'
    crawler = 'the_daily_mail'

class TheGuardian(Crawler):

    timezone = pytz.timezone('Europe/London')
    title = 'The Guardian'
    crawler = 'the_guardian'


class TheTimes(Crawler):

    timezone = pytz.timezone('Europe/London')
    title = 'The Times'
    crawler = 'the_times'
        

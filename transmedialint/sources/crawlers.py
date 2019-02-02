

from datetime import datetime
import itertools
import re

from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify
import pytz
from scrapyd_api import ScrapydAPI

from sources.models import Article, Author, Source

class Crawler(object):

    solr_url = 'http://localhost:8983/solr/articles/update/extract'
    
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
    def scrape(cls,terms):
        scrapyd = ScrapydAPI('http://localhost:6800')
        scrapyd.schedule(cls.crawler, 'search', query=terms,
            last_scraped=cls.date_last_scraped.isoformat())

        
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
    title = 'The TheTimes'
    crawler = 'the_times'
        
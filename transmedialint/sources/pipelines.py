
import logging
import re

from dateutil import parser as dateparser

from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify

from sources import models


class ArticlePipeline(object):
    
    def __init__(self):
        self.sources = {}
        self.authors = {}
        
        
    def get_source(self, name):
        source = self.sources.get(name)
        if not source:
            source = models.Source.get(name=name)
            self.sources[name] = source
        return source
    
    
    def clean_names(self, names):
        names = re.split('\s[fF][oO][rR]\s',names)[0]
        names = re.split('\s[tT][oO]\s',names)[-1]
        return re.split('[,&]|\s[aA][nN][dD]\s',names)
    
    
    def capital_name(self, name):
        return ' '.join(['-'.join([barrel.capitalize() for barrel in chunk.split('-')])
            for chunk in name.split()])


    def fetch_author(name):
        original_slug = slug = slugify(name)
        suffix = itertools.count(1)
        fetched = False
        while not fetched:
            try:
                author, created = Author.objects.get_or_create(name=name, slug=slug)
                if created:
                    author.save()
                fetched = True
            except:
                slug = original_slug + str(suffix.__next__())
        return author


    def get_authors(self,byline):
        names = list(map(self.capital_name, self.clean_names(byline)))
        
        existing = list(filter(None,map(self.authors.get,names)))
        
        new_names = set(names) - set(existing)
        
        new_authors = list(map(self.fetch_author, new_names))
        
        return existing + new_authors
        
        
    def process_item(self, item, spider):
        slug = slugify(item['title'])
        
        art, created = models.Article.objects.get_or_create(url=item['url'])
        if not created:
            logging.info('SKIPPED: '+slug)
            return item

        art.title = item['title']
        art.slug = slug
        art.source = self.get_source(item['source'])
        art.date_published = localtimsezone.localtime(dateparser.parse(
            item['date_published'])
        art.date_retrieved = localtimezone.now()
        art.page.save(slug, ContentFile(item['content']),
            save=True)
        art.author = self.get_authors(item['byline'])
        
        art.save()
        
        return item
    

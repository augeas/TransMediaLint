
import itertools
from io import BytesIO
import logging
import os
import re
from zipfile import ZipFile, ZIP_DEFLATED

from asgiref.sync import sync_to_async
from dateutil import parser as dateparser
from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify
import requests
from scrapy.exceptions import DropItem

from sources import models
from transmedialint import settings as tml_settings

SOLR_URL = 'http://{}:8983/solr/articles/update/extract'.format(
    os.environ.get('SOLR_HOST', 'localhost'))

PATTERNS = list(map(re.compile, tml_settings.DEFAULT_TERMS + ['trans']))


class ArticlePipeline(object):
    
    def __init__(self):
        self.sources = {}
        self.authors = {}
        
    def get_source(self, name):
        source = self.sources.get(name)
        if not source:
            source, created = models.Source.objects.get_or_create(name=name)
            if created:
                source.save()
            self.sources[name] = source


        return source
    

    def item_timestamp(self, item):
        return dateparser.parse(item['date_published'])

    
    def clean_names(self, names):
        names = re.split(r'\s[fF][oO][rR]\s',names)[0]
        names = re.split(r'\s[tT][oO]\s',names)[-1]
        return re.split(r'[,&]|\s[aA][nN][dD]\s',names)
    
    
    def capital_name(self, name):
        return ' '.join(['-'.join([barrel.capitalize() for barrel in chunk.split('-')])
            for chunk in name.split()])


    def fetch_author(self, name):
        original_slug = slug = slugify(name)
        suffix = itertools.count(1)
        fetched = False
        while not fetched:
            try:
                author, created = models.Author.objects.get_or_create(name=name, slug=slug)
                if created:
                    author.save()
                fetched = True
            except:
                slug = original_slug + str(suffix.__next__())
        return author


    def get_authors(self,byline):
        names = list(map(self.capital_name, self.clean_names(byline)))
        
        existing = list(filter(None,map(self.authors.get, names)))
        
        new_names = set(names) - set(existing)
        
        new_authors = list(map(self.fetch_author, new_names))
        
        return existing + new_authors
        
    @sync_to_async
    def process_item(self, item, spider):
        slug = slugify(item['title'])

        try:
            first_match = itertools.chain.from_iterable(p.finditer(item['raw'].lower())
                for p in PATTERNS).__next__()
        except:
            raise DropItem('NO MATCHES: '+slug)

        try:
            art, created = models.Article.objects.get_or_create(
                url=item['url'],
                title = item['title'],
                source = self.get_source(item['source']),
                slug = slug,
                date_published = self.item_timestamp(item),
                date_retrieved = localtimezone.now())
        except:
            raise DropItem('SKIPPED: '+slug)


        art_authors = self.get_authors(item['byline'])
        
        art.author.add(*art_authors)

        art.content.save(slug + '_content', ContentFile(item['content']))

        if item.get('preview'):
            art.preview.save(slug + '_preview', ContentFile(item['preview']))

        zip_bytes = BytesIO()
        fname = '.'.join((slug, 'html'))
        
        with ZipFile(zip_bytes, 'w') as zipfile:
            zipfile.writestr(fname, item['content'], ZIP_DEFLATED)

        art.raw.save(slug + '.zip', ContentFile(zip_bytes.getbuffer()),
            save=True)

        art.save()

        solr_fields = {}
        solr_fields['literal.id'] = art.id
        solr_fields['literal.author'] = [a.name for a in art_authors]
        solr_fields['literal.title'] = art.title
        solr_fields['literal.source'] = art.source.name
        solr_fields['literal.url'] = art.url
        solr_fields['literal.timestamp'] = item['date_published']
        solr_fields['commitWithin'] = '2000'        
        solr_files = {'file': ('article.text', item['content'])}
        requests.post(SOLR_URL, data=solr_fields, files=solr_files)
        
        item['article_id'] = art.id
        item['source_id'] = art.source.id
        
        return item
    

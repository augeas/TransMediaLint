import pytz
import requests
from bs4 import BeautifulSoup

from datetime import datetime
import itertools
import re

from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify

from .models import Article, Author, Source

class Crawler(object):

    solr_url = 'http://localhost:8983/solr/articles/update/extract'
    
    def __init__(self):
        pass
    
    @classmethod
    def get_slug(cls):
        return slugify(cls.title)

    @staticmethod
    def dedupe(key,seq):
        seenit = set()
        for item in seq:
            val = item[key]
            if val not in seenit:
                seenit.add(val)
                yield item
    
    @staticmethod
    def capital_name(name):
        return ' '.join([wrd.capitalize() for wrd in name.split()])
    
    @staticmethod
    def clean_names(names):
        names = re.split('\s[fF][oO][rR]\s',names)[0]
        names = re.split('\s[tT][oO]\s',names)[-1]
        return re.split('[,&]|\s[aA][nN][dD]\s',names)  

    @staticmethod
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

    @classmethod
    def get_authors(cls):
        store = {}
        while True:
            author_text = yield
            names = list(map(cls.capital_name, cls.clean_names(author_text)))
            existing = [store.get(name,False) for name in names]
            created = [cls.fetch_author(name) if not exist else False
                for name,exist in zip(names,existing)]
            for name, author in zip(names,created):
                if author:
                    store[name] = author
            yield [old if old else new for old,new in zip(existing,created)]

    @classmethod
    def get_article(cls,ref,author_getter,source):
        doc = requests.get(ref['url']).text
        ref['date_retrieved'] = localtimezone.now()
        soup = BeautifulSoup(doc,'html5lib')
        ref.update(cls.extract_article(soup))
        if not ref['date_published']:
            ref['date_published'] = cls.timezone.localize(datetime.combine(ref['date'], datetime.min.time()))
        fields = {k:ref[k] for k in ['title','url','date_published','date_retrieved']}
        fields['broken'] = ref.get('broken',False)
        fields['source'] = source
        slug = slugify(ref['title'])
        fields['slug'] = slug
        
        try:
            art = Article.objects.get(url=ref['url'])
        except:
            art = False
        
        if not art:
            art = Article(**fields)
            art.page.save(slug,ContentFile(doc),save=True)
            next(author_getter)
            for author in author_getter.send(ref['author']):
                art.author.add(author)
            art.save()
            solr_fields = {}
            solr_fields['literal.id'] = art.id
            solr_fields['literal.author'] = ref['author']
            solr_fields['literal.title'] = art.title
            solr_fields['literal.source'] = cls.__name__
            solr_fields['literal.url'] = art.url
            solr_fields['literal.timestamp'] = ref['date_published'].timestamp()
            solr_fields['commitWithin'] = '2000'        
            solr_files = {'file': ('article.html', doc)}
            requests.post(cls.solr_url, data=solr_fields, files=solr_files)

            print('saved '+slug)
        else:
             print('skipped '+slug)
             

    @classmethod
    def date_last_scraped(cls):
        return cls.get_object().last_scraped.date()

    @classmethod
    def scrape(cls,terms):
        author_getter = cls.get_authors()
        this_source = cls.get_object()
        for ref in cls.query(terms):
            authors = cls.get_article(ref, author_getter, this_source)
        this_source.last_scraped = localtimezone.now()
        this_source.save()
        
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

    def __init__(self):
        pass
    
    @staticmethod
    def query_term(term,page=1):
        query_url = 'https://www.thesun.co.uk/page/'+str(page)+'/?s='+term
        soup = BeautifulSoup(requests.get(query_url).text,'html5lib')
        results = soup.find_all('div', attrs={'class':'teaser-item--search'})
        return [{'teaser':item.find('p',attrs={'class':'teaser__subdeck'}).text.strip(),
            'date':datetime.strptime(item.find('div', attrs={'class':'search-date'}).text,'%d %B %Y').date(),
            'url':item.find('a')['href']} for item in results]
        
    @classmethod
    def query_all_terms(cls,terms):
        last_scraped = cls.date_last_scraped()
        for term in terms:
            result_batches = (cls.query_term(term,page=i) for i in itertools.count(1))
            results = itertools.chain.from_iterable(itertools.takewhile(lambda r: len(r)>0, result_batches))
            yield from itertools.takewhile(lambda r: r['date'] >= last_scraped, results)

    @classmethod
    def query(cls,terms):
        yield from cls.dedupe('url',cls.query_all_terms(terms))

    @classmethod
    def extract_article(cls,soup):
        ref = {}
        try:
            ref['title'] = soup.find('h1',attrs={'class':'article__headline'}).text
        except:
            ref['title'] = cls.title
            ref['broken'] = True
        
        try:
            author_span = soup.find('span',attrs={'class':'article__author-name theme__copy-color'}).text
            ref['author'] = ' '.join(author_span.split()[1:]).split(',')[0]
        except:
            ref['author'] = cls.title
            ref['broken'] = True

        try:
            date_string = soup.find('div',attrs={'class':'article__published'}).text
            day = re.match('[0-9+]',date_string).group(0).zfill(2)
            date_chunks = ' '.join([day] + re.split('[\s,]+',date_string)[1:])
            ref['date_published'] = cls.timezone.localize(datetime.strptime(date_chunks,'%d %B %Y %I:%M %p'))
        except:
            ref['date_published'] = False
            ref['broken'] = True
            
        return ref
    
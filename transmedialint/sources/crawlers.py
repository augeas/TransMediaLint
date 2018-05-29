import pytz
import requests
from bs4 import BeautifulSoup

from datetime import datetime
import dateutil.parser       
import itertools
import re
import time

from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify

from .models import Article, Author, Source

from transmedialint.settings import DEFAULT_SEARCH_TERMS, GUARDIAN_API_KEY

class Crawler(object):

    solr_url = 'http://tml_solr:8983/solr/articles/update/extract'
    
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
        return ' '.join(['-'.join([barrel.capitalize() for barrel in chunk.split('-')])
            for chunk in name.split()])

    @staticmethod
    def clean_names(names):
        names = re.split('\sfor\s',names, flags = re.IGNORECASE)[0]
        names = re.split('\sin\s',names, flags = re.IGNORECASE)[0]
        names = re.split('\sto\s',names, flags = re.IGNORECASE)[-1]
        return re.split('[,&]|\sand\s',names, flags = re.IGNORECASE)
    
    @staticmethod
    def clean_date(chunk):
        return re.match('[0-9]+',chunk).group(0).zfill(2)

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
    def extract_article(cls, *args):
        return {}

    @classmethod
    def get_article(cls,ref,author_getter,source):
        slug = slugify(ref['title'])
        try:
            art = Article.objects.get(url=ref['url'])
        except:
            art = False
        
        if art:
            print('skipped '+slug)
            return False
        
        ref['date_retrieved'] = localtimezone.now()
        
        doc = ref.get('doc',False)
        
        if not doc:
            doc = requests.get(ref['url']).text
            soup = BeautifulSoup(doc,'html5lib')
            ref.update(cls.extract_article(soup,ref))
            
        fields = {k:ref[k] for k in ['title','url','date_published','date_retrieved']}
        fields['broken'] = ref.get('broken',False)
        fields['source'] = source
        fields['slug'] = slug
        
        art = Article(**fields)
        art.page.save(slug,ContentFile(doc),save=True)
        art.preview.save(slug,ContentFile(ref['preview']),save=True)
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

        return True

    @classmethod
    def date_last_scraped(cls):
        return cls.get_object().last_scraped.date()

    @classmethod
    def scrape(cls,terms=DEFAULT_SEARCH_TERMS):
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
    
    @classmethod
    def render_item(cls,item):
        return {'teaser':item.find('p',attrs={'class':'teaser__subdeck'}).text.strip(),
            'date':datetime.strptime(item.find('div', attrs={'class':'search-date'}).text,'%d %B %Y').date(),
            'url':item.find('a')['href'], 'preview':str(item)}
    
    @classmethod
    def query_term(cls,term,page=1):
        query_url = 'https://www.thesun.co.uk/page/'+str(page)+'/?s='+term
        soup = BeautifulSoup(requests.get(query_url).text,'html5lib')
        results = soup.find_all('div', attrs={'class':'teaser-item--search'})
        return [cls.render_item(item) for item in results]
        
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
    def extract_article(cls,soup,ref):
        fields = {}
        try:
            fields['title'] = soup.find('h1',attrs={'class':'article__headline'}).text
        except:
            fields['title'] = cls.title
            fields['broken'] = True
        
        try:
            author_span = soup.find('span',attrs={'class':'article__author-name theme__copy-color'}).text
            fields['author'] = ' '.join(author_span.split()[1:]).split(',')[0]
        except:
            fields['author'] = cls.title
            fields['broken'] = True

        try:
            date_string = soup.find('div',attrs={'class':'article__published'}).text
            day = cls.clean_date(date_string)
            date_chunks = ' '.join([day] + re.split('[\s,]+',date_string)[1:])
            fields['date_published'] = cls.timezone.localize(datetime.strptime(date_chunks,'%d %B %Y %I:%M %p'))
        except:
            fields['date_published'] = cls.timezone.localize(datetime.combine(ref['date'], datetime.min.time()))
            fields['broken'] = True
            
        return fields
    
class TheDailyMail(Crawler):

    timezone = pytz.timezone('Europe/London')
    title = 'The Daily Mail'
   
    field_getters = {'title':lambda s: s.find('h3', attrs={'class':'sch-res-title'}).text,
        'author': lambda s: s.find('h4', attrs={'class':'sch-res-info'}).find('a').text,
        'url': lambda s: ''.join(['http://www.dailymail.co.uk',
        s.find('h3', attrs={'class':'sch-res-title'}).find('a')['href']]),
        'preview':lambda s: str(s)}
   
    @classmethod
    def parse_date(cls,soup):
        date_chunks = soup.find('h4', attrs={'class':'sch-res-info'}).text.split()[-5:]
        date_chunks[1] = cls.clean_date(date_chunks[1])
        date_chunks[3] = ':'.join(map(lambda c: c.zfill(2), date_chunks[3].split(':')))
        date_string = ' '.join(date_chunks)
        return cls.timezone.localize(datetime.strptime(date_string,'%B %d %Y, %I:%M:%S %p'))     
    
    @classmethod
    def render_item(cls,item):
        rendered = {}
        for k,f in cls.field_getters.items():
            try:
                rendered[k] = f(item)
            except:
                rendered['broken'] = True
        try:
            rendered['date_published'] = cls.parse_date(item)
        except:
            rendered['broken'] = True
        return rendered
    
    @classmethod
    def query_chunks(cls,terms,page_size=50):
        phrase = '+or+'.join(terms)
        offset = (page_size * page for page in itertools.count(0))
        while True:
            url = '?'.join(['http://www.dailymail.co.uk/home/search.html',
                'offset={}&size={}&sel=site&searchPhrase={}&sort=recent&type=article&days=all'.format(
                next(offset), page_size, phrase)])
            soup = BeautifulSoup(requests.get(url).text,'html5lib')
            results = soup.find_all('div', attrs={'class':'sch-result'})
            yield [cls.render_item(r) for r in results]    

    @classmethod
    def extract_article(cls,soup,ref):
        fields = {}
        
        for k,f in {'title':lambda s: s.find('div',attrs={'id':'js-article-text'}).find('h1').text,
            'author': lambda s: s.find('p',attrs={'class':'author-section'}).find('a').text}.items():
            if not ref.get(k,False):
                try:
                    fields[k] = f(soup)
                except:
                    fields[k] = cls.title
                    fields['broken'] = True
                    
        if not ref.get('date_published',False):
            try:
                date_string = ' '.join(soup.find('span',
                    attrs={'class':'article-timestamp-published'}).text.split()[-4:])
                fields['date_published'] = cls.timezone.localize(
                    datetime.strptime(date_string,'%H:%M, %d %B %Y'))
            except:
                pass

        return fields
            
    @classmethod
    def query(cls,terms):
        last_scraped = cls.get_object().last_scraped
        chunker = itertools.takewhile(lambda c: len(c) > 0, cls.query_chunks(terms))
        items = itertools.chain.from_iterable(chunker)
        yield from itertools.takewhile(lambda i: i['date_published'] >= last_scraped,items)
 
class TheGuardian(Crawler):
     
    timezone = pytz.timezone('Europe/London')
    title = 'The Guardian'

    @classmethod
    def query_chunks(cls,terms,page_size=50):
        q = ' OR '.join(terms)
        payload = {'q':q, 'api-key':GUARDIAN_API_KEY, 'page-size':page_size, 'order-by':'newest',
            'show-fields':'byline,shortUrl,body'}
        
        def get_chunk(page):
            params = {'page':page}
            params.update(payload)
            req = requests.get('https://content.guardianapis.com/search', params=params)
            time.sleep(0.2)
            return req.json().get('response', {})
        
        all_chunks = map(get_chunk, itertools.count(1))

        chunks = itertools.takewhile(lambda r: r.get('currentPage',1) <= r.get('pages',-1),
            all_chunks)
        
        yield from map(lambda c: c['results'], chunks)
        
    @classmethod
    def render_item(cls,item):
        fields = {'title':'webTitle', 'url':'webUrl', 'preview':'webTitle'}
        rendered = {k:item[i] for k,i in fields.items()}
        extra_fields = {'doc':'body', 'author':'byline'}
        rendered.update({k:item['fields'].get(i,'') for k,i in extra_fields.items()})
        rendered['date_published'] = dateutil.parser.parse(item['webPublicationDate'])
        return rendered

    @classmethod
    def query(cls, terms):
        this_source = cls.get_object()
        all_articles = itertools.chain.from_iterable(cls.query_chunks(terms))
        all_rendered = map(cls.render_item, all_articles)
        yield from itertools.takewhile(lambda a: a['date_published'] > this_source.last_scraped, all_rendered)
        
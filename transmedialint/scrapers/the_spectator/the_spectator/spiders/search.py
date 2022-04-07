

import logging
import re

from dateutil import parser
import scrapy

from scrapers.article_items import ArticleItem
from transmedialint import settings as tml_settings


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)
SCRIPT_URL = 'http://www.spectator.co.uk/main.js'
SEARCH_URL = ('https://host-w86kbp.api.swiftype.com/'
    +'/api/as/v1/engines/live-spectator/search.json')

SEARCH_DATA = {
    'facets': {'author': {'type': 'value', 'size': 10},
    'type': {'type': 'value', 'size': 10}},
    'result_fields': {'tags': {'raw': {},
    'snippet': {'size': 300, 'fallback': True}},
    'author': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'byline': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'text_body': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'hero_image': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'url': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'created_at': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'updated_at': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'date': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'title': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}},
    'id': {'raw': {}, 'snippet': {'size': 300, 'fallback': True}}},
    'sort': {'date': 'desc'}
}


class SearchSpider(scrapy.Spider):
    name = 'search'
    source = 'The Spectator'
    
    
    def __init__(self, *args, **kwargs):
        query = kwargs.get('query', DEFAULT_QUERY)
        logging.info('SEARCHING THE SPECTATOR FOR :{}'.format(query))
        self.terms = query.split()
        self.headers = {}
        super().__init__(*args, **kwargs)
        
        
    def start_requests(self):
        yield scrapy.Request(url=SCRIPT_URL, callback=self.parse_script)
        
        
    def parse_script(self, response):
        search_key, = re.findall('(?<=this.searchKey="search-)[^"]+',
            response.text)
        
        self.headers = {'authorization': 'Bearer search-{}'.format(search_key)}
        
        for term in self.terms:
            query = {'query': term, 'page': {'current': 1, 'size': 20}}
            yield scrapy.http.JsonRequest(url=SEARCH_URL, headers=self.headers,
                data={**query, **SEARCH_DATA}, method='POST', dont_filter=True,
                callback=self.parse_results, meta={'term': term})
            
            
    def parse_results(self, response):
        resp = response.json()
        
        items = resp.get('results', [])
        fields = {'title': 'title', 'byline': 'author', 'content': 'text_body',
            'date_published': 'date', 'url': 'url'}
        for item in items:
            article = dict(map(lambda f: (f[0], item.get(f[1])['raw']),
                fields.items()))
            article['date_published'] = parser.parse(article['date_published']).isoformat()
            article['preview'] = item['text_body'].get('snippet')
            article['url'] = 'https://www.spectator.co.uk' + article['url']
            article['source'] = 'The Spectator'
            
            yield ArticleItem(**article)

        term = response.meta['term']
            
        this_page = resp['meta']['page']['current']
        page_size = resp['meta']['page']['size']

        if items:
            query = {'query': term, 'page': {
                'current': this_page+1, 'size': page_size}}
            
            yield scrapy.http.JsonRequest(url=SEARCH_URL, headers=self.headers,
                data={**query, **SEARCH_DATA}, method='POST', dont_filter=True,
                callback=self.parse_results, meta={'term': term})
            

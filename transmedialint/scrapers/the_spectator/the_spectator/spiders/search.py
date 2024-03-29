
import logging
import re

from dateutil import parser
import scrapy
from scrapy_selenium import SeleniumRequest

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
        yield SeleniumRequest(url='https://www.spectator.co.uk', callback=self.parse_script)
        
        
    def parse_script(self, response):
        driver = response.request.meta['driver']

        retries = 0
        search_key = ''

        while retries < 5 and not search_key:
            driver.get(SCRIPT_URL)
            try:
                logging.info('THE SPECTATOR: WAITING FOR SEARCH-KEY...')
                search_key, = re.findall('(?<=this.searchKey="search-)[^"]+',
                    driver.page_source)
            except:
                retries += 1

        self.headers = {'authorization': 'Bearer search-{}'.format(search_key)}
        
        for term in self.terms:
            query = {'query': term, 'page': {'current': 1, 'size': 20}}
            yield scrapy.http.JsonRequest(url=SEARCH_URL, headers=self.headers,
                data={**query, **SEARCH_DATA}, method='POST', dont_filter=True,
                callback=self.parse_results, meta={'term': term})
            
            
    def parse_results(self, response):

        '''
        anchors = response.xpath('//article').css(
            'header.article__header>h3>a.article__title-link')

        links = anchors.xpath('@href').extract()
        titles =  list(map(str.strip, anchors.xpath('text()').extract()))
        previews = response.css('p.article__excerpt-text').xpath('text()')
        bylines = list(map(str.strip, response.css('a.article__author').xpath(
            'text()').extract()))
        ''''


        resp = response.json()
        
        items = resp.get('results', [])
        fields = {'title': 'title', 'byline': 'author', 'date_published': 'date', 'url': 'url'}
        for item in items:
            article = {k: item.get(v).get('raw') for k, v in fields.items()}
            article['content'] = item['text_body']['raw']
            article['date_published'] = parser.parse(article['date_published']).isoformat()
            article['preview'] = item['text_body'].get('snippet')
            article['url'] = 'https://www.spectator.co.uk' + article['url']
            article['source'] = 'The Spectator'

            article['raw'] = response.text

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
            

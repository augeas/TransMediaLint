
from datetime import datetime
import logging

from dateutil import parser
import scrapy

from scrapers.article_items import ArticleItem
from transmedialint import settings as tml_settings


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)

SEARCH_URL ='https://unherd.com/?s={}'

class SearchSpider(scrapy.Spider):
    name = 'search'
    source = 'Unherd'
    
    
    def __init__(self, *args, **kwargs):
        query = kwargs.get('query', DEFAULT_QUERY)
        logging.info('SEARCHING UNDERD FOR :{}'.format(query))
        self.terms = query.split()
        super().__init__(*args, **kwargs)
        
        
    def start_requests(self):
        
        for term in self.terms:
            yield scrapy.Request(url=SEARCH_URL.format(term),
                meta={'term': term, 'page': 1},
                callback=self.parse_results)
            
            
    def parse_results(self, response):
        titles = response.css('h4.title').xpath('a/@title').extract()
        urls = response.css('h4.title').xpath('a/@href').extract()
        bylines = response.css('p.author-meta').xpath('a/text()').extract()
        
        items = [dict(zip(('title', 'url', 'byline'), res))
            for res in zip(titles, urls, bylines)]

        yield from (scrapy.Request(url=item['url'], meta=item,
            callback=self.parse_article) for item in items)
        
        next_page = response.meta.get('page', 1) + 1
        
        max_page = response.meta.get('max_page',
            int(response.css('ul.pagination').xpath(
            'li/a/text()')[-2].extract())
        )

        term = response.meta['term']
        
        if next_page <= max_page:
            url = 'https://unherd.com/page/{}/?s={}'.format(next_page, term)
            yield scrapy.Request(url=url,
                meta={'term': term, 'page': page, 'max_page': max_page},
                callback=self.parse_results)
            
        
    def parse_article(self, response):
        try:
            date_published = parser.parse(response.css('div.date').xpath(
                'text()').extract_first()).isoformat()
        except:
            logging.error('UNHERD: BROKEN DATE FOR: {}'.format(response.url))
            date_published = None

        preview = response.css('div.metabox').xpath(
            'h4/text()').extract_first()

        content = '\n'.join(response.css('div#artbody').xpath(
            'div/p/text()').extract())
        
        item = {k: response.meta.get(k) for k in
            ('title', 'url', 'byline')}
        
        item['date_published'] = date_published
        item['preview'] = preview
        item['content'] = content
        item['raw'] = response.text
        item['source'] = 'Unherd'
        
        if date_published:
            yield ArticleItem(**item)

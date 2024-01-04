
# Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt

from datetime import datetime
from itertools import takewhile
import logging

from dateutil import parser
import scrapy

from scrapers.article_items import ArticleItem
from transmedialint import settings as tml_settings


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)

SEARCH_URL ='https://unherd.com/?s={}'

not_comment = lambda p: not p.xpath('preceding::div[starts-with(@class, "wpd-comment")]')

def content_p(ptags):
    return '\n'.join(filter(None, (p.xpath('text()').extract_first()
        for p in takewhile(not_comment, ptags)))).strip()

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
                meta={'term': term, 'page': next_page, 'max_page': max_page},
                callback=self.parse_results)
        
    def parse_article(self, response):
        try:
            date_published = parser.parse(response.xpath(
                '//meta[@name="cXenseParse:publishtime"]/@content').extract_first()).isoformat()
        except:
            logging.error('UNHERD: BROKEN DATE FOR: {}'.format(response.url))
            date_published = None

        preview = response.css('div.metabox').xpath(
            'h4/text()').extract_first()
        
        if not preview:
            description_xp = '//meta[@property="og:description"]/@content'
            preview = response.xpath(description_xp).extract_first().split('[')[0]

        content = '\n'.join(response.css('div#artbody').xpath(
            '//p/span/text()').extract()).strip()
        
        if not content:
            content = content_p(response.css('div#artbody').xpath('//p'))
        
        if not content:
            content = content_p(response.css('div.thepostinner').xpath('//p'))

        if not content:
            logging.error('UNHERD: MISSING CONTENT FOR: {}'.format(response.url))

        item = {k: response.meta.get(k) for k in
            ('title', 'url', 'byline')}
        
        item['date_published'] = date_published
        item['preview'] = preview
        item['content'] = content
        item['raw'] = response.text
        item['source'] = 'Unherd'
        
        if date_published and content:
            yield ArticleItem(**item)

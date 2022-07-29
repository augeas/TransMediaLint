
from datetime import datetime
import logging

from dateutil import parser
import scrapy

from scrapers.article_items import ArticleItem
from transmedialint import settings as tml_settings


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)


class SearchSpider(scrapy.Spider):
    name = "search"
    
    
    def __init__(self, *args, **kwargs):
        query = kwargs.get('query', DEFAULT_QUERY)
        if query:
            self.terms = query.split()
        else:
            self.terms = []
        assert self.terms
        self.last_scraped = kwargs.get('last_scraped',
            datetime.fromtimestamp(0).isoformat())
        
        super().__init__(*args, **kwargs)
        
        
    def start_requests(self):
        urls = list(map('https://www.thesun.co.uk/?s={}'.format,
            self.terms))
                
        yield from (scrapy.Request(url=u, callback=self.parse,
            meta={'page': 1, 'term': t}) for u, t in zip(urls,self.terms))

        
    def parse(self, response):
        page = response.meta['page'] + 1
        
        timestamps = (parser.parse(t) for t in
            response.css('.search-date').xpath('./text()').extract())
        
        urls = response.css('.teaser-anchor--search').xpath(
            './@href').extract()

        new = list(filter(lambda t: t[0].isoformat() > self.last_scraped,
            zip(timestamps, urls)))
        
        if new:
            yield from (scrapy.Request(url=u, callback=self.parse_article)
                for t, u in new)
        
            url = 'https://www.thesun.co.uk/page/{}/?s={}'.format(page,
                response.meta['term'])
        
            yield scrapy.Request(url=url, callback=self.parse,
                meta={'page': page, 'term': response.meta['term']})
        
        
    def parse_article(self, response):
        timestamp = parser.parse(response.xpath('//time/@datetime').extract_first()).isoformat()

        try:
            author = response.css('.author')[0].xpath('@data-author').extract_first()
        except:
            author = response.css('.article__author-name').xpath('text()').extract_first()
        
        title = response.css('.article__headline')[0].xpath(
            './text()').extract_first()

        preview = response.xpath('//meta[@name="description"]/@content').extract_first()

        content = '\n'.join(response.css('div.article__content')[0].xpath(
            'descendant::p|span|h2|a').xpath('text()').extract())

        yield ArticleItem(**{'title': title, 'byline': author,
            'preview': preview, 'url': response.url,'date_published': timestamp,
            'content': content, 'raw': response.text, 'source': 'The Sun'})


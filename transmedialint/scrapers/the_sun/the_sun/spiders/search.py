
from datetime import datetime
import json
import logging
import re

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
            meta={'term': t}) for u, t in zip(urls,self.terms)
        )

    async def parse(self, response):
        term = response.meta['term']
        page = response.meta.get('page', 1)

        results = response.css('div.teaser__copy-container')
        urls = map(
            'https://www.thesun.co.uk{}'.format,
            results.xpath('a/@href').extract()
        )

        preview_h3 = results.css('h3.teaser__subdeck').xpath(
            '@data-original-text').extract()
        preview_p = results.css('p.teaser__lead').xpath('text()').extract()
        previews = list(map('\n'.join,zip(preview_h3, preview_p)))

        for url, preview in zip(urls, previews):
            yield scrapy.Request(
                url, meta={'preview': preview},
                callback=self.parse_article
            )

        logging.info('THE SUN: SEARCH {} PAGE {}'.format(
            term, page)
        )

        page += 1
        yield scrapy.Request(
            'https://www.thesun.co.uk/page/{}/?s={}'.format(page, term),
            meta={'page': page, 'term': term}, callback=self.parse,
        )

    async def parse_article(self, response):
        jdata = json.loads(response.xpath(
            '//script[@type="application/ld+json"]/text()').extract_first()
        )
        timestamp = parser.parse(jdata['datePublished']).isoformat()
        title = jdata['headline']
        author = jdata['author'][0]['name']
        content = '\n'.join(
            response.css('div.article__content>p').xpath('text()').extract()
        )

        logging.info('THE SUN: {}'.format(title))

        yield ArticleItem(**{'title': title, 'byline': author,
            'preview': response.meta.get('preview'), 'url': response.url,
            'date_published': timestamp,'content': content,
            'raw': response.text, 'source': 'The Sun'}
        )

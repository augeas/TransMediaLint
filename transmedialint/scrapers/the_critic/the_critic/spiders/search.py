
import logging

from dateutil import parser
import scrapy

from scrapers.article_items import ArticleItem
from transmedialint import settings as tml_settings


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)
SEARCH_URL = 'https://thecritic.co.uk/search/{}/page/{}/'


class SearchSpider(scrapy.Spider):
    name = 'search'
    source = 'The Critic'

    def __init__(self, *args, **kwargs):
        query = kwargs.get('query', DEFAULT_QUERY)
        logging.info('SEARCHING THE CRITIC FOR :{}'.format(query))
        self.terms = query.split()
        super().__init__(*args, **kwargs)

    def start_requests(self):

        for term in self.terms:
            yield scrapy.Request(url=SEARCH_URL.format(term, 1),
                meta={'term': term, 'page': 1},
                callback=self.parse_results)

    async def parse_results(self, response):
        wanchors = response.css('a.card-v2__title-link')

        titles = wanchors.xpath('text()').extract()
        urls = wanchors.xpath('@href').extract()
        bylines = response.css('a.author').xpath('text()').extract()
        previews = response.css(
            'div.card-v2__excerpt>p'
        ).xpath('text()').extract()

        items = [dict(zip(('title', 'url', 'byline', 'preview'), res))
            for res in zip(titles, urls, bylines, previews)]

        for req in (scrapy.Request(url=item['url'], meta=item,
            callback=self.parse_article) for item in items):
            yield req

        page = response.meta.get('page', 1) + 1
        term = response.meta['term']

        if items:
            yield scrapy.Request(url=SEARCH_URL.format(term, page),
                meta={'term': term, 'page': page},
                callback=self.parse_results)

    async def parse_article(self, response):
        try:
            date_published = parser.parse(
                response.xpath('//time/@datetime').extract_first()).isoformat()
        except:
            date_published = None

        content = ''.join(
            filter(None, response.css('div.sf-article-content__text').xpath(
            'descendant::*/text()').extract())
        ).strip()

        item = {k: response.meta.get(k) for k in
            ('title', 'url', 'byline', 'preview')}

        item['date_published'] = date_published
        item['content'] = content
        item['raw'] = response.text
        item['source'] = 'The Critic'

        if date_published:
            yield ArticleItem(**item)

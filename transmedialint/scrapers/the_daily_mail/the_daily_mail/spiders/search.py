
from datetime import datetime
from itertools import chain
import logging

from dateutil import parser
import scrapy

from scrapers.article_items import response_article
from transmedialint import settings as tml_settings

base_url = 'https://www.dailymail.co.uk/home/search.html'
search_args = ('offset={}&size={}&sel=site&searchPhrase={}'
    +'&sort=recent&type=article&days=all',)

DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
    + '(KHTML, like Gecko) Version/16.6 Safari/605.1.1')

class SearchSpider(scrapy.Spider):
    name = 'search'
    source = 'The Daily Mail'

    def __init__(self, query=DEFAULT_QUERY, last_scraped=None, **kwargs):
        logging.info('SEARCHING THE DAILY MAIL FOR :{}'.format(query))
        self.terms = query.split()
        if last_scraped:
            self.last_scraped = last_scraped
        else:
            self.last_scraped = datetime.fromtimestamp(0).isoformat()
        super().__init__(**kwargs)

        self.user_agent = UA
        self.cookies = {}

    def start_requests(self):
        yield from self.search_pages(offset=0, terms=self.terms)

    def search_pages(self, offset, terms=None):
        if not terms:
            terms = self.terms
        urls = ('?'.join([base_url, search_args.format(offset, 50, term)]) for term
            in terms)
        return (scrapy.Request(url=url, callback=self.parse,
            headers = {'User-Agent': self.user_agent}, cookies=self.cookies,
            meta={'offset': offset, 'term': term}, dont_filter=True)
            for url, term in zip(urls, terms))

    def parse(self, response):
        offset = response.meta.get('offset', 0)
        next_offset = 50 + offset
        search_term = response.meta.get('term')
        logging.info('DAILY MAIL: {} NEXT OFFSET: {}'.format(
            search_term, next_offset))

        titles = response.css('h3.sch-res-title').xpath('a/text()').extract()

        urls = ['https://www.dailymail.co.uk' + u if not u.startswith('/wires')
            else None for u in response.css('h3.sch-res-title').xpath(
            'a/@href').extract()
        ]

        previews = response.css('p.sch-res-preview').xpath('text()').extract()

        bylines  = [res.xpath('a/text()[1]').extract_first()
            for res in  response.css('h4.sch-res-info')]

        timestamps = [ts.isoformat() for ts in
            map(parser.parse, response.css('h4.sch-res-info').xpath(
            'text()[last()]').extract())
        ]

        meta = ({'title': title, 'url': url, 'preview': preview,
            'byline': byline, 'date_published': timestamp} for
            title, url, preview, byline, timestamp in
            zip(titles, urls, previews, bylines, timestamps))
        
        valid_meta = filter(lambda m: all(m.values()), meta)
        
        new = filter(lambda m: m['date_published'] > self.last_scraped,
            valid_meta)
        
        requests = [scrapy.Request(url=m['url'], callback=self.parse_article,
            headers = {'User-Agent': self.user_agent}, cookies=self.cookies,
            meta=m) for m in new]

        if len(requests):
            logging.info('DAILY MAIL: {} FOUND {} ARTICLES AT OFFSET {}'.format(
                search_term, len(requests), offset))
            yield from requests
            yield from self.search_pages(next_offset, terms=(search_term,))
        else:
            logging.info("DAILY MAIL: {}, NO RESULTS FROM: {}".format(
                search_term, response.url))
      
    def parse_article(self, response):
        content = '\n'.join(response.css('p.mol-para-with-font').xpath(
            'text()').extract())
        if not content:
            content = ' '.join(filter(None, chain.from_iterable(
                map(str.split, response.xpath(
                '//div[@itemprop="articleBody"]/descendant::text()').extract()))))

        yield response_article(self.source, response,
            content=content)

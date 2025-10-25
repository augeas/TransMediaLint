
from datetime import datetime
from itertools import chain
import json
import logging
import os
import re

from dateutil import parser
import scrapy
from scrapy_playwright.page import PageMethod

from scrapers.article_items import ArticleItem
from transmedialint import settings as tml_settings


SEARCH_URL = 'https://www.thetimes.co.uk/search?source=search-page&q={}'
SEARCH_PAGE_URL = 'https://www.thetimes.co.uk/search?p={}&q={}&source=search-page'


class TimesSpider(scrapy.Spider):
    name = 'search'
    start_urls = ['https://www.thetimes.com/']

    def __init__(self, **kwargs):

        query = kwargs.get('query', None)
        if query:
            self.terms = query.split()
        else:
            self.terms = None
            
        logging.info(self.terms)
        
        try:
            self.last_scraped = parser.parse(
                kwargs.get('last_scraped', None)).isoformat()
        except:
            self.last_scraped = datetime.fromtimestamp(0).isoformat()
        
        self.username = kwargs.get('username',
            os.environ.get('TIMES_USERNAME'))
        self.password = kwargs.get('password',
            os.environ.get('TIMES_PASSWORD'))
        
        super().__init__(**kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],
            meta={
                'playwright': True,
                'playwright_include_page': True
            },
            callback=self.login
        )
                              
    async def login(self, response):
        page = response.meta["playwright_page"]

        await page.frame_locator(
            'xpath=//iframe[starts-with(@id,"sp_message")]').locator(
            'button.sp_choice_type_13').click()
        logging.info('TIMES: COOKIE CONSENT')
        await page.locator('xpath=//a/span[text()="Login"]').click()
        logging.info('TIMES: LOGIN BUTTON')
        try:
            await page.locator('xpath=//input[@id="1-email"]').fill(self.username)
            logging.info('TIMES: USERNAME')
        except:
            await page.screenshot(path='/transmedialint/article_dump/times_email_bork.png')
        try:
            await page.locator('xpath=//input[@aria-label="Password"]').fill(self.password)
            logging.info('TIMES: PASSWORD')
        except:
            await page.screenshot(path='/transmedialint/article_dump/times_pw_bork.png')
        await page.locator('css=button.auth0-lock-submit').click()
        logging.info('TIMES: LOGIN BUTTON')
        try:
            await page.locator('xpath=//a/span[text()="My account"]').click()
            logging.info('TIMES: LOGGED IN')
        except:
            await page.screenshot(path='/transmedialint/article_dump/times_account_bork.png')

        search_url = 'https://www.thetimes.co.uk/search?source=nav-desktop&q={}'

        for term in tml_settings.DEFAULT_TERMS:
            url = search_url.format(term)
            meta = {'term': term, 'page': 1}
            yield scrapy.Request(url, meta=meta, callback=self.parse_search)

    def parse_search(self, response):
        results = response.css('ul.SearchResultList>li')

        titles = results.css('h2').xpath('a/text()').extract()
        bylines = results.css('strong.Byline-name').xpath('text()').extract()
        dates_published = map(datetime.isoformat,
            map(parser.parse, results.css('span.Dateline').xpath('text()').extract()))
        previews = (' '.join(el.xpath('child::text()').extract())
            for el in results.css('p.Item-dip'))
        urls = map('https://www.thetimes.co.uk/{}'.format,
            results.css('h2').xpath('a/@href').extract())

        items = list(dict(zip(('title', 'url', 'byline', 'preview', 'date_published'), res))
            for res in zip(titles, urls, bylines, previews, dates_published))

        new_items = list(filter(lambda i: i['date_published'] > self.last_scraped, items))

        for item in new_items:
            yield scrapy.Request(item['url'], meta=item, cookies=self.cookies,
                headers={'User-Agent': self.user_agent}, callback=self.parse_article)

        if len(items):
            next_page = response.meta['page'] + 1

            term = response.meta['term']
            url = 'https://www.thetimes.co.uk/search?p={}&q={}&source=nav-desktop'
            meta = {'term': term, 'page': next_page}

            yield scrapy.Request(url.format(next_page, term), meta=meta, cookies=self.cookies,
                headers={'User-Agent': self.user_agent}, callback=self.parse_search)


    def extract_text(self, node):
        if node['name'] == 'text':
            yield node['attributes']['value']

        yield from chain.from_iterable(map(self.extract_text, node['children']))


    def parse_article(self, response):

        item = {k: response.meta.get(k) for k in
            ('title', 'url', 'byline', 'preview', 'date_published')}

        item['source'] = 'The Times'

        logging.info('The Times: scraped "{}"'.format(item['title']))

        apollo_xp = '//script[starts-with(text(), "window.__APOLLO_STATE__")]/text()'
        try:
            apollo = json.loads(response.xpath(apollo_xp).extract_first().lstrip(
                '__window.__APOLLO_STATE__ = ')[:-1])
        except:
            logging.warning('The Times: No valid JSON for {}'.format(item['url']))
            apollo = None

        if not apollo is None:
            article = chain.from_iterable(re.findall('Article:[a-z0-9\-]+$', k)
                for k in apollo.keys()).__next__()

            item['content'] = '\n'.join(chain.from_iterable(
                map(self.extract_text, apollo[article]['paywalledContent']['json'])))

            item['raw'] = response.text

            yield ArticleItem(**item)




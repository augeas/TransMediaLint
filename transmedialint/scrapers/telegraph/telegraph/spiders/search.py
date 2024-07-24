
from datetime import datetime
import json
import logging
import os
import re

from dateutil import parser
import scrapy
from scrapy_playwright.page import PageMethod

from scrapers.article_items import ArticleItem
from transmedialint import settings as tml_settings

SEARCH_JSON = {
    "exact": True ,"active": True, "sort-by": "date", "sort-dir": "desc",
    "from": 0, "size": 12, "snippets": True, "sources": ["aem"],
    "allows":[], "blocks": ["betting", "financial-services"]
}

class TelegraphSpider(scrapy.Spider):
    name = 'search'

    def __init__(self, **kwargs):

        query = kwargs.get('query', None)
        if query:
            self.terms = query.split()
        else:
            self.terms = tml_settings.DEFAULT_TERMS

        try:
            self.last_scraped = parser.parse(
                kwargs.get('last_scraped', None)).isoformat()
        except:
            self.last_scraped = datetime.fromtimestamp(0).isoformat()

        self.username = kwargs.get('username',
            os.environ.get('TELEGRAPH_USERNAME'))
        self.password = kwargs.get('password',
            os.environ.get('TELEGRAPH_PASSWORD'))

        assert self.username and self.password

        #super().__init__(**kwargs)

    def start_requests(self):
        yield scrapy.Request(
            'https://secure.telegraph.co.uk/customer/secure/login',
            callback=self.login,
            meta={
                'playwright': True,
                'playwright_include_page': True,
                'playwright_page_methods': [
                    PageMethod('wait_for_selector', 'iframe[title~="Consent"]'),
                ]
            }
        )

    async def login(self, response):
        page = response.meta["playwright_page"]

        await page.frame_locator('[title~="Consent"]').locator(
            'div.buttons-desktop>button[aria-label~="No,"]').click()

        await page.locator('input[name="email"]').fill(self.username)
        await page.locator('button[id="login-button"]').click()
        await page.locator('input[name="password"]').fill(self.password)
        await page.locator('button[id="login-button"]').click()
        await page.locator(
            'div.e-site-header-button--sign-in>a.e-site-header-button__link'
        ).click()
        logging.info('TELEGRAPH: LOGGED IN')


        for term in self.terms:
            search_pars = SEARCH_JSON.copy()
            search_pars['terms'] = term

            yield scrapy.Request(
                'https://api.telegraph.co.uk/content-text-search/v2',
                method="POST",
                body = json.dumps(search_pars),
                meta = {'term': term, 'offset': 0},
                headers = {'Content-Type': 'application/json; charset=UTF-8'},
                callback=self.search
            )

        await page.close()

    async def search(self, response):
        results = json.loads(response.body)
        hits = results.get('hits', [])
        term = response.meta['term']
        offset = response.meta.get('offset', 0)

        logging.info('TELEGRAPH: {} results for {} from {}.'.format(
            len(hits), term, offset)
        )

        for article in hits:
            yield scrapy.Request(
                article['url'],
                meta={'article': article, 'term': term},
                callback=self.parse_article
            )

        total_hits = results.get('total', 0)
        next_page = offset + results.get('query', {}).get('size', 0)
        if total_hits > next_page:
            search_pars = SEARCH_JSON.copy()
            search_pars['terms'] = term
            search_pars['from'] = next_page

            yield scrapy.Request(
                'https://api.telegraph.co.uk/content-text-search/v2',
                method="POST",
                body = json.dumps(search_pars),
                meta = {'term': term, 'offset': next_page},
                headers = {'Content-Type': 'application/json; charset=UTF-8'},
                callback=self.search
            )

    async def parse_article(self, response):
        content = ''.join(response.css('div.article-body-text').xpath(
            'descendant::text()').extract())

        result = response.meta['article']

        byline = result.get('authors')
        title = result.get('headline')
        date_published = parser.parse(result.get('date')).isoformat()

        try:
            title =  response.css('h1.e-headline').xpath(
                'text()').extract_first().strip()
        except:
            title = response.xpath(
                '//meta[@name="twitter:description"]/@content').extract_first()

        article = {
            'content': content, 'byline': byline, 'title': title,
            'date_published': date_published, 'preview': title,
            'raw': response.text, 'url': response.url,
            'source': 'The Telegraph'
        }

        logging.info('TELEGRAPH: scraped {}'.format(article['title']))

        yield ArticleItem(**article)


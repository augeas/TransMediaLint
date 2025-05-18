
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
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/103.0.5060.53 Safari/537.36'

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
        
        self.cookies = {}

        super().__init__(**kwargs)



    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],
            meta={
                'playwright': True,
                'playwright_include_page': True
            },
            callback=self.login
        )
                              
    def accept_cookies(self, driver):
        logging.info('The Times: Waiting for cookie button...')

        try:
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                'button.sp_choice_type_11')))
        except:
            return False

        button.click()
        logging.info('The Times: Approved cookies...')
        return True


    def send_email(self, driver):
        email = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH,
            '//input[@name="email"]')))

        logging.info('The Times: Found email field.')

        try:
            email.send_keys(self.username)
            return True
        except:
            return False


    def login_script(self, driver):
        frame = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
            '//iframe[starts-with(@id,"sp_message")]')))

        driver.switch_to.frame(frame)

        self.accept_cookies(driver)

        button = None

        driver.switch_to.default_content()

        anchor = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
            'a.GlobalMenu-conversionLink--logIn')))

        logging.info('The Times: Logging in...')

        anchor.click()

        email_okay = self.send_email(driver)
        while not email_okay:
            self.accept_cookies(driver)
            email_okay = self.send_email(driver)

        pw = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH,
            '//input[@name="password"]')))

        pw.send_keys(self.password)

        login = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH,
            '//button[@name="submit"]')))

        login.click()

        logged_in =  WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
            '//a[@aria-controls="my-account-menu"]')))

        logging.info('The Times: Logged in...')

        self.cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        self.user_agent = driver.execute_script("return navigator.userAgent")

        return True



    async def login(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.frame_locator(xpath='//iframe[starts-with(@id,"sp_message")]')


        await page.frame_locator('[title~="Consent"]').locator(
            'div.buttons-desktop>button[aria-label~="No,"]').click()
        logging.info('TELEGRAPH: COOKIE CONSENT')
        await page.locator('input[name="email"]').fill(self.username)
        await page.locator('button[id="login-button"]').click()
        logging.info('TELEGRAPH: USERNAME')
        await page.locator('input[name="password"]').fill(self.password)
        await page.locator('button[id="login-button"]').click()
        logging.info('TELEGRAPH: PASSWORD')
        logging.info('TELEGRAPH: LOGGED IN')
       
        
        
        
        
        driver = response.request.meta['driver']

        try:
            logged_in = self.login_script(driver)
        except:
            logged_in = False

        search_url = 'https://www.thetimes.co.uk/search?source=nav-desktop&q={}'

        if logged_in:
            for term in tml_settings.DEFAULT_TERMS:

                url = search_url.format(term)
                meta = {'term': term, 'page': 1}
                yield scrapy.Request(url, meta=meta, cookies=self.cookies,
                    headers={'User-Agent': self.user_agent}, callback=self.parse_search)
        else:
            yield SeleniumRequest(url=self.start_urls[0], callback=self.login)


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




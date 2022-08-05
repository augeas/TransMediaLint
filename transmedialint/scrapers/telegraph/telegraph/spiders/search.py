
from datetime import datetime
import json
import logging
import os
import re

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.article_items import ArticleItem


class TelegraphSpider(scrapy.Spider):
    name = 'search'
    start_urls = ['https://www.telegraph.co.uk/']

    def __init__(self, **kwargs):
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/103.0.5060.53 Safari/537.36'
        self.cookies = {}

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
            os.environ.get('TELEGRAPH_USERNAME'))
        self.password = kwargs.get('password',
            os.environ.get('TELEGRAPH_PASSWORD'))

        assert self.username and self.password

        self.cookies = {}
        self.cx = ''
        self.cse_token = ''
        self.cse_version = ''

        super().__init__(**kwargs)


    def start_requests(self):
        yield SeleniumRequest(url=self.start_urls[0], callback=self.login)


    def login(self, response):
        driver = response.request.meta['driver']

        frame = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
            '//iframe[starts-with(@id,"sp_message")]'))
        )

        logging.info('TELEGRAPH: switching to iframe...')
        driver.switch_to.frame(frame)

        button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
            '//button[@title="Accept"]'))
        )

        logging.info('TELEGRAPH: accepting cookies...')
        driver.execute_script("arguments[0].click();", button)

        driver.switch_to.default_content()

        login = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
            'div.e-site-header-button--sign-in>a'))
        )

        logging.info('TELEGRAPH: starting log-in...')
        login.click()

        email = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
            '//input[@name="email"]'))
        )

        logging.info('TELEGRAPH: sending username...')
        email.send_keys(self.username)

        cont = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
            '//button[@id="login-button"]'))
        )

        cont.click()

        pw = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
            '//input[@id="password"]'))
        )

        logging.info('TELEGRAPH: sending password...')
        pw.send_keys(self.password)

        cont = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
            '//button[@id="login-button"]'))
        )

        cont.click()

        logged_in = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,
            '//button[@aria-label="Open profile modal"]'))
        )

        logging.info('TELEGRAPH: logged in')

        self.cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        self.user_agent = driver.execute_script("return navigator.userAgent")

        scr = response.css('div.component-content').xpath('script/text()').extract_first()
        self.cx = re.findall('(?<=var cx = ")[^"]+', scr)[0]

        yield scrapy.request('https://cse.google.com/cse.js?cx={}'.format(self.cx),
            headers = {'User-Agent': self.user_agent},
            callback = self.parse_script)


    def cse_request(self, term, num=20, start=0):
        pars = {
            'rsz': 'filtered_cse', 'num': str(num), 'hl': 'en',
            'source': 'gcsc', 'gss': '.uk',
            'cselibv': self.cse_version, 'cx': self.cx, 'q': term,
            'safe': 'active', 'cse_tok': self.cse_token, 'sort': 'date',
            'exp': 'csqr,cc', 'callback': 'google.search.cse.api'
        }

        if start:
            pars['start'] = str(start)

        search_url = 'https://cse.google.com/cse/element/v1'

        return scrapy.FormRequest(search_url, method='GET', formdata=pars,
            meta = {'term': term, 'start': start}, dont_filter = True,
            callback = self.parse_results)


    def parse_script(self, response):
        self.cse_token = re.findall('(?<="cse_token": ")[^"]+', response.text)[0]
        self.cse_version = re.findall('(?<="cselibVersion": ")[^"]+', response.text)[0]

        for term in self.terms:
            yield self.cse_request(term)


    def parse_results(self, response):
        try:
            results = json.loads(re.split('google.search.cse.api\(',
                response.text)[-1][:-2])
        except:
            results = []

        for result in results:
            yield scrapy.Request(result['url'], cookies=self.cookies,
                headers={'User-Agent': self.user_agent},
                callback=self.parse_article)

        if results:
            term = response.meta['term']
            start = response.meta.get('start', 0) + 20

            yield self.cse_request(term, start=start)


    def parse_article(self, response):
        article = {
            'content': ''.join(response.css('div.article-body-text').xpath(
                'descendant::text()').extract()),
            'byline': response.css('span.e-byline__author').xpath(
                '@content').extract_first(),
            'title':    response.css('h1.e-headline').xpath(
                'text()').extract_first().strip(),
            'date_published': response.css('time.e-published-date').xpath(
                '@datetime').extract_first(),
            'preview': response.css('p.e-standfirst').xpath(
                'text()').extract_first().strip(),
            'raw': response.text,
            'source': 'The Telegraph'
        }

        logging.info('TELEGRAPH: scraped {}'.format(article['title']))

        yield ArticleItem(**item)



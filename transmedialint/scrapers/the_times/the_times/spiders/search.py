
from datetime import datetime
import logging
import os

from dateutil import parser
import scrapy
from scrapy_splash import SplashRequest


__LOGIN_SCRIPT__ = '''
function form_input(splash, sel, text)
  el = splash:select(sel)
  b = el:bounds()
  splash:mouse_click((b.left+b.right)/2, (b.top+b.bottom)/2)
  assert(splash:wait(0.5))
  splash:send_keys(text)
end

function wait_for_it(splash, sel)
  while not splash:select(sel)
  do
    assert(splash:wait(0.5))
  end
end

function main(splash, args)
  splash:init_cookies(splash.args.cookies)
  assert(splash:go('https://www.thetimes.co.uk/'))
  wait_for_it(splash, 'iframe')
    
  splash:runjs("document.getElementsByTagName('iframe')[1].contentDocument.getElementsByClassName('message-button')[1].click()")
  
  assert(splash:go('https://login.thetimes.co.uk/?gotoUrl=https://www.thetimes.co.uk/'))
 
  wait_for_it(splash, 'input[aria-label="Email"]')
  wait_for_it(splash, 'input[aria-label="Password"]')
 
  form_input(splash, 'input[aria-label="Email"]', args.username)
  assert(splash:wait(0.5))  
    
  form_input(splash, 'input[aria-label="Password"]', args.password)
  assert(splash:wait(0.5))

  form_input(splash, 'input[aria-label="Email"]', args.username)
  assert(splash:wait(0.5))  
  
  wait_for_it(splash, 'button.auth0-lock-submit')
  
  splash:select('button.auth0-lock-submit'):mouse_click()
  
  wait_for_it(splash, 'a[aria-controls="my-account-menu"]')
  
  entries = splash:history()
  last_response = entries[#entries].response  
  
  return {
    url = splash:url(),
    html = splash:html(),
    http_status = last_response.status,
    headers = last_response.headers,
    png = splash:png(),
    har = splash:har(),
    cookies = splash:get_cookies(),
  }
end
'''


SEARCH_URL = 'https://www.thetimes.co.uk/search?source=search-page&q={}'
SEARCH_PAGE_URL = 'https://www.thetimes.co.uk/search?p={}&q={}&source=search-page'

class TimesSpider(scrapy.Spider):
    name = 'search'
    start_urls = ['https://www.thetimes.co.uk']


    def __init__(self, **kwargs):
        query = kwargs.get('query', None)
        if query:
            self.terms = query.split()
        else:
            self.terms = None
            
        logging.info(self.terms)
        
        try:
            self.last_scraped = parser.parse(kwargs.get('last_scraped', None))
        except:
            self.last_scraped = datetime.fromtimestamp(0)
        
        self.username = kwargs.get('username',
            os.environ.get('TIMES_USERNAME'))
        self.password = kwargs.get('password',
            os.environ.get('TIMES_PASSWORD'))
        
        super().__init__(**kwargs)


    def start_requests(self):
        yield SplashRequest(self.start_urls[0], callback=self.after_login,
            endpoint='/execute', args={
                'lua_source': __LOGIN_SCRIPT__, 'timeout': 60,
                'username': self.username, 'password': self.password},
            meta = {'splash': {'session_id': 1}})


    def after_login(self, response):
        #headers = {k.encode('ascii'): v.encode('ascii')
        #    for k,v in response.headers.items()}

        print(headers)
        
        cookies = {c.name: c.value for c in response.cookiejar}
        for term in self.terms:
            yield scrapy.Request(url=SEARCH_URL.format(term),
                callback=self.parse_search,
                meta={'page': 1, 'term': term, 'splash_cookies': cookies})
                                 

    def parse_search(self, response):
        results = response.css('h2.Item-headline').xpath('a/@href').extract()
        dates = list(map(parser.parse,
            response.css('span.Item-dateline').xpath('text()').extract())) 

        new_results = [res for res, dt in zip(results, dates)
            if dt > self.last_scraped]       
        
        for res in new_results:
            #print('https://www.thetimes.co.uk'+res)
            yield scrapy.Request(url='https://www.thetimes.co.uk'+res,
                callback = self.parse_article,
                cookies=response.meta['splash_cookies'])

        if len(response.xpath('//a[@aria-label="Next page"]')):
            next_page = response.meta['page'] + 1
            term = response.meta['term']
            yield scrapy.Request(url=SEARCH_PAGE_URL.format(next_page, term),
                callback=self.parse_search,
                meta={'page': next_page, 'term': term,
                    'splash_cookies': response.meta['splash_cookies']})
        

    def parse_article(self, response):
        #print(response.url)
        try:
            byline = response.css('meta[name="author"]').xpath(
                '@content').extract_first().split('by ')[-1]
        except:
            byline = 'The Times'
        
        title = response.css('meta[property="og:title"]').xpath(
            '@content').extract_first()
        
        timestamp = parser.parse(response.xpath(
            '//time/@datetime').extract()[-1]).isoformat()
        
        preview = response.xpath('//h2[@role="heading"]/text()').extract_first()    

        print('ARTICLE: {}'.format(title))
        if response.xpath('//a[aria-controls="my-account-menu"]').extract():
            print('LOGGED IN...')
        
        if response.xpath('//div[@id="paywall-portal-page-footer"]').extract():
            print('PAYWALL...')

        yield {'title': title, 'url': response.url, 'preview': preview,
            'byline': byline, 'date_published': timestamp,
            'content': response.text, 'source': 'The Times'}

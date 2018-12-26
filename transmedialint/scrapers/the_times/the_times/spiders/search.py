
from datetime import datetime

import scrapy

class LoginSpider(scrapy.Spider):
    name = 'search'
    start_urls = ['https://login.thetimes.co.uk/']


    def __init__(self, **kwargs):
        query = kwargs.get('query', None)
        if query:
            self.terms = '+OR+'.join(query.split())
        else:
            self.terms = None
        self.last_scraped = kwargs.get('last_scraped', None)    
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('query', None)


    def parse(self, response):
        if self.username and self.password:
            return scrapy.FormRequest.from_response(response,
                formdata={'username': self.username, 'password': self.password},
                callback=self.after_login)


    def after_login(self, response):
        if self.terms:
            url = 'https://www.thetimes.co.uk/search?q={}'.format(self.terms)
            
            yield scrapy.Request(url=url, callback=self.parse_search,
            meta={'page': 1})
            
            
    def parse_search(self, response):
        next_page = response.meta['page'] + 1
        
        results = response.css('.Item-headline').xpath('./a/@href').extract()
        urls =  ('https://www.thetimes.co.uk' + res for res in results)
        
        datespans = response.css('.Item-dateline').xpath('./text()').extract()
        timestamps = (datetime.strptime(ds,'%A %B %d  %Y').isoformat()
            for ds in datespans)
        
        new = list(filter(lambda u,t: t>self.last_scraped,
            zip(urls, timestamps)))
        
        #publications = response.css('.Item-publication').xpath(
        #    './text()').extract()

        if new:
            yield from (scrapy.Request(url=url, callback=self.parse_article)
            for url,t in new)
            
            url = 'https://www.thetimes.co.uk/search?p={}&q={}'.format(
                next_page, self.terms)
            
            yield scrapy.Request(url=url, callback=self.parse_search,
                meta={'page': next_page})
            

    def parse_article(self, response):
        timespan = response.css('.Dateline').xpath('./text()').extract()[0]
        timestamp = datetime.strptime(','.join(timespan.split(',')[0:2]),
            '%B %d %Y, %I:%M%p').isoformat()
        byline = response.css('.Byline-name--article').xpath('./text()').extract()


        #yield {'page': response.text}
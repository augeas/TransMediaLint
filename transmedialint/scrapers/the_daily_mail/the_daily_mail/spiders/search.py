
from datetime import datetime
import logging

import scrapy

from transmedialint import settings as tml_settings

base_url = 'http://www.dailymail.co.uk/home/search.html'
search_args = 'offset={}&size={}&sel=site&searchPhrase={}&sort=recent&type=article&days=all'


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)


class SearchSpider(scrapy.Spider):
    name = 'search'
    
    
    def __init__(self, query=DEFAULT_QUERY, last_scraped=None, **kwargs):
        logging.info('SEARCHING THE DAILY MAIL FOR :{}'.format(query))
        self.terms = '+or+'.join(query.split())
        if last_scraped:
            self.last_scraped = last_scraped
        else:
            self.last_scraped = datetime.fromtimestamp(0).isoformat()
        super().__init__(**kwargs)    
    
            
    def start_requests(self):
        url = '?'.join([base_url, search_args.format(0, 50, self.terms)])
        logging.info(url)
        yield scrapy.Request(url=url, callback=self.parse, meta={'offset': 0})
        
        
    def parse(self, response):
        next_offset = 50 + response.meta.get('offset', 0)
        
        articles = response.css('.sch-res-content')
        anchors = articles.xpath('./h3').css('.sch-res-title').xpath(
            './a')
        titles = anchors.xpath('./text()').extract()
        urls = ('https://www.dailymail.co.uk'+u for u in
            anchors.xpath('./@href').extract())
        
        previews = articles.css('.sch-res-preview').xpath('./text()').extract()

        info = articles.xpath('./h4').css('.sch-res-info')        
        bylines = info.xpath('./a/text()').extract()

        timechunks = map(str.split,map(str.strip, info.xpath(
            './text()[last()]').extract()))
                
        timestr = (' '.join([t[1]] + [''.join(filter(str.isdigit,t[2]))]
            + t[3:]) for t in timechunks)

        timestamps = (datetime.strptime(t, '%B %d %Y, %I:%M:%S %p'
            ).isoformat() for t in timestr)
        
        meta = ({'title': title, 'url': url, 'preview': preview,
            'byline': byline, 'date_published': timestamp} for
            title, url, preview, byline, timestamp in
            zip(titles, urls, previews, bylines, timestamps))
        
        new = filter(lambda m: m['date_published'] > self.last_scraped, meta)
        
        requests = [scrapy.Request(url=m['url'], callback=self.parse_article,
            meta=m) for m in new]
        
        if requests:
            yield from requests
            url = '?'.join([base_url, search_args.format(
                next_offset, 50, self.terms)])
            yield scrapy.Request(url=url, callback=self.parse,
                meta={'offset': next_offset})
        
        
    def parse_article(self, response):
        logging.info('DAILY MAIL: SCRAPED: {} '.format(response.meta['title']))
        yield {**response.meta, **{'content': response.text,
            'source': 'The Daily Mail'}}
        


from datetime import datetime
import logging

import scrapy


base_url = 'http://www.dailymail.co.uk/home/search.html'
search_args = 'offset={}&size={}&sel=site&searchPhrase={}&sort=recent&type=article&days=all'


class SearchSpider(scrapy.Spider):
    name = 'search'
            
    def start_requests(self):
        logging.info(self.query)
        logging.info('START')
        terms = '+or+'.join(self.query.split())
        logging.info(terms)
        url = '?'.join([base_url, search_args.format(0, 50, terms)])
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
        yield {**response.meta, **{'content': response.text,
            'source': 'The Daily Mail'}}
        

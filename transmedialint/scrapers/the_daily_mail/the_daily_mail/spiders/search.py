
from datetime import datetime
import logging

import scrapy

from scrapers.article_items import response_article
from transmedialint import settings as tml_settings

base_url = 'https://www.dailymail.co.uk/home/search.html'
search_args = 'offset={}&size={}&sel=site&searchPhrase={}&sort=recent&type=article&days=all'


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)


def search_item_date(ts):
    try:
        return datetime.strptime(ts, '%B %d %Y, %I:%M:%S %p').isoformat()
    except:
        return None


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


    def search_pages(self, offset, terms=None):
        if not terms:
            terms = self.terms
        urls = ('?'.join([base_url, search_args.format(offset, 50, term)]) for term
            in terms)
        return (scrapy.Request(url=url, callback=self.parse,
            meta={'offset': offset, 'term': term}, dont_filter=True)
            for url, terms in zip(urls, terms))
        
    
    def start_requests(self):
        yield from self.search_pages(0)
        
        
    def parse(self, response):
        offset = response.meta.get('offset', 0)
        next_offset = 50 + offset
        search_term = response.meta.get('term')
        logging.info('DAILY MAIL: {} NEXT OFFSET: {}'.format(
            search_term, next_offset))
        
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

        timestamps = map(search_item_date, timestr)
        
        meta = ({'title': title, 'url': url, 'preview': preview,
            'byline': byline, 'date_published': timestamp} for
            title, url, preview, byline, timestamp in
            zip(titles, urls, previews, bylines, timestamps))
        
        valid_meta = filter(lambda m: all(m.values()), meta)
        
        new = filter(lambda m: m['date_published'] > self.last_scraped, valid_meta)
        
        requests = [scrapy.Request(url=m['url'], callback=self.parse_article,
            meta=m) for m in new]

        if len(requests):
            logging.info('DAILY MAIL: {} FOUND {} ARTICLES AT OFFSET {}'.format(
                search_term, len(requests). offset))
            yield from requests
            yield from self.search_pages(next_offset, terms=(search_term,))
        else:
            logging.info("DAILY MAIL: {}, NO RESULTS FROM: {}".format(
                search_term, response.url))
      
      
    def parse_article(self, response):        
        yield response_article(self.source, response)

        

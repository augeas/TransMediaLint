
from datetime import datetime
import logging

from dateutil import parser
import scrapy

from scrapers.article_items import response_article
from transmedialint import settings as tml_settings


DEFAULT_QUERY = ' '.join(tml_settings.DEFAULT_TERMS)
SEARCH_URL = 'https://www.spiked-online.com/wp-admin/admin-ajax.php'


class SearchSpider(scrapy.Spider):
    name = 'search'
    source = 'Spiked'
    

    def __init__(self, *args, **kwargs):
        query = kwargs.get('query', DEFAULT_QUERY)
        logging.info('SEARCHING SPIKED FOR :{}'.format(query))
        self.terms = query.split()
        super().__init__(*args, **kwargs)
        

    def search_request(self, term, offset=0):
        return scrapy.FormRequest(url=SEARCH_URL,
            formdata={
                'action': 'load_more_posts', 'query_type': 'search',
                'offset': str(offset), 'search': term
            },
            callback=self.parse_results, meta={'term': term, 'offset': offset},
            dont_filter=True)

        
    def start_requests(self):
        yield from map(self.search_request, self.terms)


    def parse_results(self, response):
        
        authors = response.css(
            'div.compressed-mobile>div.post>h4.title-xxs>a').xpath(
            'text()').extract()

        title_headers = response.css('div.compressed-mobile>div.post>a.block>h3.title-sm')

        titles = [' '.join(t.xpath('descendant-or-self::*/text()').extract()).strip()
            for t in title_headers]
            
        published_xp = ('div.compressed-mobile>div.post>'
            +'a.block>div.post-meta>div.post-date')
        published = list(map(datetime.isoformat, map(parser.parse, response.css(
            published_xp).xpath('text()').extract())))

        links = response.css('div.compressed-mobile>div.post>a.block').xpath(
            '@href').extract()
        
        if len(authors) == len(titles) == len(published) == len(links):
            articles = zip(authors, titles, published, links)
            for author, title, date_pub, url in articles:
                yield scrapy.Request(url, callback=self.parse_article,
                    meta={
                        'byline': author, 'title': title, 'url': url,
                        'date_published': date_pub, 'preview': None
                    })
                
            if len(titles):
                offset = response.meta.get('offset', 0) + len(titles)
                logging.info('SPIKED, NEXT OFFSET: {}'.format(offset))
                yield self.search_request(response.meta['term'], offset)
                
                
    def parse_article(self, response):
        logging.info('SPIKED: SCRAPED: {} '.format(response.meta['title']))

        content = ''.join(response.css('div.cms').xpath(
            'descendant::*/text()').extract())
        
        yield response_article(self.source, response, content=content)

            
            

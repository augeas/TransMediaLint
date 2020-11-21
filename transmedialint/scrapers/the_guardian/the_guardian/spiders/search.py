
from datetime import datetime
import json
import os

from dateutil import parser
import scrapy


class SearchSpider(scrapy.Spider):
    name = 'search'

    base_url = ('https://content.guardianapis.com/search?api-key={}&q={}'
        +'&page={}&page-size=50&order-by=newest'
        +'&show-fields=byline,publication,headline,body')
    
    
    def __init__(self, **kwargs):
        query = kwargs.get('query', None)
        if query:
            self.terms = '%20OR%20'.join(query.split())
        else:
            self.terms = None
        
        if kwargs.get('last_scraped'):
            self.last_scraped = kwargs['last_scraped']
        else:
            self.last_scraped = datetime.fromtimestamp(0).isoformat()

        
        self.key = kwargs.get('key', os.environ.get('GUARDIAN_KEY'))
        
        super().__init__(**kwargs)
            
            
    def start_requests(self):
        url = self.base_url.format(self.key, self.terms, 1)
        yield scrapy.Request(url=url, callback=self.parse)
        
        
    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        
        page = json_response['response']['currentPage']
    
        results = ({**r, **{'timestamp': parser.parse(
            r['webPublicationDate']).isoformat()}} for r in  
            json_response['response']['results'])
     
        new_results = list(filter(lambda r: r['timestamp']>self.last_scraped,
            results))
        
        if new_results:
        
            yield from ({'source': 'The Guardian',
                'title': res['fields']['headline'],
                'byline': res['fields'].get('byline', 'The Guardian'),
                'date_published': res['timestamp'],
                'url': res['webUrl'],
                'content': res['fields']['body']}
                for res in new_results)
        
            if page < json_response['response']['pages']:
                url = self.base_url.format(self.key, self.terms, page+1)
                yield scrapy.Request(url=url, callback=self.parse) 


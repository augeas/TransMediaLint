

import json

from dateutil import parser
import scrapy


class SearchSpider(scrapy.Spider):
    name = 'search'

    base_url = ('https://content.guardianapis.com/search?api-key={}&q={}'
        +'&page={}&page-size=50&show-fields=byline&show-fields=publication'
        +'&show-fields=headline&show-fields=body')
    
    
    def __init__(self, **kwargs):
        query = kwargs.get('query', None)
        if query:
            self.terms = '%20OR%20'.join(query.split())
        else:
            self.terms = None
        self.last_scraped = kwargs.get('last_scraped', None)
        self.key = kwargs.get('key', None)
            
            
    def start_requests(self):
        url = base_url.format(self.key, self.terms, 1)
        yield scrapy.Request(url=url, callback=self.parse)
        
        
    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        
        page = json_response['response']['currentPage']
    
        results = ({**r, **{'timestamp': parser.parse(
            r['webPublicationDate']).isoformat()}} for r in  
            json_response['results'])
     
        new_results = filter(lambda r: r['timestamp']>self.last_scraped,
            results)
        
        yield from ({'source': 'TheGuardian',
            'title': res['fields']['headline'],
            'byline': res['fields']['byline'],
            'date_published': res['timestamp'],
            'url': res['webUrl'],
            'content': res['fields']['body']}
            for res in new_results)
        
        if page < json_response['pages']:
            url = base_url.format(self.key, self.terms, page+1)
            yield scrapy.Request(url=url, callback=self.parse) 


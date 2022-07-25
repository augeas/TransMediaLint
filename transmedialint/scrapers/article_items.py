
import json
import logging

from scrapy.item import Item, Field


class ArticleItem(Item):
    title = Field()
    byline = Field()
    url = Field()
    date_published = Field()
    preview = Field()
    content = Field()
    raw = Field()
    source = Field()
    
    source_id = Field()
    article_id = Field()
    doc = Field()

    def __repr__(self):
        r = {}
        for attr, value in self.__dict__['_values'].items():
            if attr not in ('content', 'raw', 'created', 'source_id', 'article_id', 'doc'):
                r[attr] = value
        return json.dumps(r, sort_keys=True, indent=4, separators=(',', ': '))
    
    
def response_article(source, response):
    logging.info('{}: SCRAPED: {} '.format(source.upper(),
        response.meta['title']))
    
    item = {'source': source, 'raw': response.text}
    
    for attr in ('title', 'byline', 'url', 'date_published', 'content'):
        item[attr] = response.meta.get(attr)
        
    return ArticleItem(**item)

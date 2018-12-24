import scrapy


class SearchSpider(scrapy.Spider):
    name = "search"
    
    
    def __init__(self, **kwargs):
        query = kwargs.get('query', None)
        if query:
            self.terms = query.split()
        else:
            self.terms = []
        
        
    def start_requests(self):
        urls = map;p('https://www.thesun.co.uk/?s={}'.format,
            self.terms)
        
        
        
        yield from (scrapy.Request(url=u, callback=self.parse,
            meta={'page': 1, 'term': t}) for u, t in zip(urls,self.terms))

        
    def parse(self, response):
        page = response.meta['page'] + 1
        
        url = 'https://www.thesun.co.uk/page/{}/?s={}'.format(page,
            response.meta['term'])
        
        yield scrapy.Request(url=url, callback=self.parse, meta={'page': page,
            'term': response.meta['term']})
        
        
    def parse_article(self, response):
        datespan, timespan = response.css('.article__published')[0].xpath('./span/text()').extract()
        
        day, month, year = datespan.split()
        
        day_str = ''.join(([0] + list(filter(str.isdigit,day)))[-2:])

        time_str = ' '.join([day_str,month,year,timespan.strip()])
        timestamp = datetime.strptime(time_str, '%d %B %Y, %I:%M %p')

        
        authorspan =  response.css('.article__author-name')[0].xpath(
            './text()').extract()[0]
        
        author = ' '.join(authorspan.split()[1:]).split(',')[0]
        
        title = response.css('.article__headline')[0].xpath(
            './text()').extract()[0]

        teaser = response.css('.article__kicker').xpath('./text()').extract()[0]

        yield {}


    
#response.css('.teaser-anchor--search').xpath('./@href').extract()
#response.css('.search-date').xpath('./text()').extract()


        
        



import scrapy


class SearchSpider(scrapy.Spider):
    name = 'search'

    base_url = 'http://www.dailymail.co.uk/home/search.html'
    search_args = 'offset={}&size={}&sel=site&searchPhrase={}&sort=recent&type=article&days=all'

    def __init__(self, **kwargs):
        query = kwargs.get('query', None)
        if query:
            self.terms = '+or+'.join(query.split())
        else:
            self.terms = None
            
            
    def start_requests(self):
        url = '?'.join([base_url, search_args.format(0, 50, self.terms)])
        yield scrapy.Request(url=url, callback=self.parse, meta={'offset': 0})
        
        
    def parse(self, request):
        articles = art=response.css('.sch-res-content')
        anchors = articles.xpath('./h3').css('.sch-res-title').xpath(
            './a/@href')
        titles = anchors.xpath('./text()').extract()
        urls = anchors.xpath('./@href').extract()
        
        previews = articles.css('.sch-res-preview').xpath('./text()').extract()

        info = articles.xpath('./h4').css('.sch-res-info')        
        bylines = info.xpath('./a/text()').extract()

        timechunks = map(str.split,map(str.strip, info.xpath(
            './text()[last()]').extract()))
                
        timestr = (' '.join([t[1]] + [''.join(filter(str.isdigit,t[2]))]
            + t[3:]) for t in timechunks)

        timestamps = (datetime.strptime(t, '%B %d %Y, %I:%M:%S %p'
            ).isoformat() for t in timestr)

        
     

        
        
        
        
        
  

            
            

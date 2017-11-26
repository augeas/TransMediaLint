from django.test import TestCase

from .crawlers import Crawler

class CrawlerCleanTestCase(TestCase):
    
    def test_name_extraction(self):        
        horace = 'Horace Streeb-Greebling'

        self.assertEqual(Crawler.capital_name('HORACE STREEB-GREEBLING'), horace)
        self.assertEqual(Crawler.capital_name('horace streeb-greebling'), horace)
        
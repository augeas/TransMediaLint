
from django.core.management.base import BaseCommand

from sources.models import Source, Article
from tml_corpus.models import ArticleEntity
from tml_corpus.pipelines import NERPipeline


class Command(BaseCommand):
    
    def find_entities(self, source):
        self.stdout.write('Finding entities for {}...'.format(
            source.name))
        
        pipeline = NERPipeline()
        
        articles = Article.objects.filter(source=source)
        
        for article in articles.iterator():
            ArticleEntity.objects.filter(article=article).delete()
            
            try:
                pipeline.process_item(article.as_item(), None)
                self.stdout.write('found entities for: {}'.format(
                    article.slug))
            except:
                self.stdout.write('could not find entities for: {}'.format(
                    article.slug))

            
            
            
        
        
    def add_arguments(self, parser):
        parser.add_argument('slugs', nargs='+', type=str)
        
        
    def handle(self, *args, **options):
        
        for source_slug in options.get('slugs', []):
            try:
                source = Source.objects.get(slug=source_slug)
                self.find_entities(source)
            except:
                source = None

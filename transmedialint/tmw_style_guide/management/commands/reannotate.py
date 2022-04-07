

from django.core.management.base import BaseCommand

from sources.models import Source, Article
from tmw_style_guide.models import Annotation, RatedArticle
from tmw_style_guide.pipelines import TMLintPipeline


class Command(BaseCommand):
    
    def reannotate(self, source):
        self.stdout.write('Re-annotating articles for {}...'.format(
            source.name))
        
        pipeline = TMLintPipeline()
        articles = Article.objects.filter(source=source)

        #self.stdout.write('{} articles'.format(len(articles)))

        for article in articles.iterator():
            Annotation.objects.filter(article=article).delete()
            RatedArticle.objects.filter(article=article).delete()
            try:
                pipeline.process_item(article.as_item(), None)
                self.stdout.write('re-annotated: {}'.format(
                    article.slug))
            except:
                self.stdout.write('could not reannotate: {}'.format(
                    article.slug))
            

    def add_arguments(self, parser):
        parser.add_argument('slugs', nargs='+', type=str)

    
    def handle(self, *args, **options):
        
        for source_slug in options.get('slugs', []):
            try:
                source = Source.objects.get(slug=source_slug)
                self.reannotate(source)
            except:
                source = None
                
            

            

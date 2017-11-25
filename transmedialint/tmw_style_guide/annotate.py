from collections import namedtuple
from datetime import datetime
import re

from django.utils import timezone as localtimezone

from .models import AnnotatedSource, Annotation 
from .rules import regexRules

from sources.models import Article

Annot = namedtuple('Annotation', ['text', 'pos', 'tag', 'label'])

def annotate(doc):
    for rule in regexRules:
        for match in re.finditer(rule.rule, doc):
            yield Annot(match.group(), match.span()[0], rule.tag, rule.label)
            
def get_annotations(crawler):
    source = crawler.get_object()
    annot_source = AnnotatedSource.objects.get_or_create(source=source)
    articles = Article.objects.filter(date_retrieved__gt=annot_source.last_updated)
    annotated_articles = filter(lambda x: len(x[1])> 0, ((art, list(annotate(art.text()))) for art in articles))
    for article, annotations in annotated_articles:
        for annot in annotations:
            art, created = Annotation.objects.get_or_create(article=article, text=annot.text, tag=annot.tag, position = annot.pos, label=annot.label)
            if created:
                art.save()
                
    annot_source.last_updated = localtimezone.now()
            
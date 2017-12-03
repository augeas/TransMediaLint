from collections import namedtuple
from datetime import datetime
import itertools
import re

from django.utils import timezone as localtimezone

from .models import AnnotatedSource, Annotation, RatedArticle
from .rules import rules, rule_tags

from sources.models import Article

Annot = namedtuple('Annotation', ['text', 'pos', 'tag', 'label'])

def annotate(doc):
    for rule in rules:
        for match in rule.rule.finditer(doc):
            yield Annot(match.group(), match.span()[0], rule.tag, rule.label)
            
def get_annotations(crawler):
    source = crawler.get_object()
    annot_source, created = AnnotatedSource.objects.get_or_create(source=source)
    articles = Article.objects.filter(source=source, date_retrieved__gt=annot_source.last_updated)
    annotated_articles = filter(lambda x: len(x[1])> 0, ((art, list(annotate(art.text()))) for art in articles))
    
    #annotated_articles = (art, list(annotate(art.text()))) for art in articles)
    
    for article, annotations in annotated_articles:
        for annot in annotations:
            obj, created = Annotation.objects.get_or_create(article=article, text=annot.text, tag=annot.tag, position = annot.pos, label=annot.label)
            if created:
                obj.save()
        rated = {tag:len(list(count)) for tag, count in itertools.groupby(sorted([a.tag for a in annotations]))}
        #if sum(rated.values()) == 0:
        #    rated['rating'] = 'green'
        if sum([rated.get(t,0) for t in rule_tags[:-1]]) == 0:
            rated['rating'] = 'yellow'
        else:
            rated['rating'] = 'red'
        rated['article'] = article
        obj, created = RatedArticle.objects.get_or_create(**rated)
        if created:
            obj.save()
                
    annot_source.last_updated = localtimezone.now()
    annot_source.save()
            

from collections import namedtuple
import itertools
import logging
import re

from dateutil import parser as dateparser

from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify
import html2text

from sources import models as source_models
from tmw_style_guide import rules, models as tmw_models


Annot = namedtuple('Annotation', ['text', 'pos', 'tag', 'label'])


class TMLintPipeline(object):
    
    def __init__(self):
        self.ann_sources = {}
        self.authors = {}
        
        
    def get_source(self, name):
        source = self.ann_sources.get(name)
        if not source:
            orig_source = source_models.Source.get(name=name)
            annot_source, created = AnnotatedSource.objects.get_or_create(
                source=orig_source)
            self.ann_sources[name] = annot_source
        return source


    def annotate(self, doc):
        for rule in rules.rules:
            for match in rule.rule.finditer(doc):
                yield Annot(match.group(), match.span()[0],
                    rule.tag, rule.label)

        
    def process_item(self, item, spider):
        
        art_id = item.get('article_id')
        if not art_id:
            return item
        
        raw_text = html2text.html2text(item['content'])
        
        annotations = list(self.annotate(raw_text))
        
        for annot in annotations:
            obj, created = tmw_models.Annotation.objects.get_or_create(
                article__id = item['article_id'],
                tag = annot.tag,
                text = annot.text,
                position = annot.pos,
                label = annot.label)
                
        rated = {tag:len(list(count)) for tag, count in
            itertools.groupby(sorted([a.tag for a in annotations]))}
        
        if sum([rated.get(t,0) for t in rules.rule_tags[:-1]]) == 0:
            if rated.get(rules.rule_tags[-1], 0) == 0:
                rated['rating'] = 0
            else:
                rated['rating'] = 'yellow'
        else:
            rated['rating'] = 'red'
            
        rated['article_id'] = art_id
        
        obj, created = tmw_models.RatedArticle.objects.get_or_create(**rated)
        
        return item

from collections import namedtuple
import itertools
import logging
import re

from dateutil import parser as dateparser
from django.core.files.base import ContentFile
from django.utils import timezone as localtimezone
from django.utils.text import slugify
import html2text
from scrapy.exceptions import DropItem
import spacy

from sources import models as source_models
from tmw_style_guide import rules, models as tmw_models


__nlp__ = spacy.load("en_core_web_sm") 


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
                
                
    def transgender_noun(self, tok):
        return tok.pos_ == 'NOUN' and tok.text.lower() == 'transgender'
    

    def process_item(self, item, spider):
        
        art_id = item.get('article_id', False)
        
        raw_text = html2text.html2text(item['content'])
        
        annotations = list(self.annotate(raw_text))

        doc = __nlp__(raw_text)
        
        noun_tokens = filter(self.transgender_noun, doc)

        noun_annotations = [
            Annot(tok.text, tok.pos, 'offensive', 'transgender as a noun')
            for tok in noun_tokens
        ]

        for annot in annotations + noun_annotations:
            try:
                obj, created = tmw_models.Annotation.objects.get_or_create(
                    article_id = item['article_id'],
                    tag = annot.tag,
                    text = annot.text,
                    position = annot.pos,
                    label = annot.label)
            except:
                raise DropItem("CAN'T ANNOTATE: "+item['title'])

            if created:
                obj.save()
                
        rated = {tag: len(list(count)) for tag, count in
            itertools.groupby(sorted([a.tag for a in annotations
            if a.label != 'transgender as a noun']))
        }
        
        if sum([rated.get(t,0) for t in rules.rule_tags[:-1]]) == 0:
            if rated.get(rules.rule_tags[-1], 0) == 0:
                rated['rating'] = 'green'
            else:
                rated['rating'] = 'yellow'
        else:
            rated['rating'] = 'red'
            
        rated['article_id'] = art_id
        
        try:
            obj, created = tmw_models.RatedArticle.objects.get_or_create(**rated)
        except:
            raise DropItem("EXISTING RATED ARTICLE: "+item['title'])


        if created:
            obj.save()
        
        item['doc'] = doc
        
        return item

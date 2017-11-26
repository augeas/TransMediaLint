from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render

from rest_framework import generics

from sources.models import Article, Author
from .models import Annotation

from . import serializers

class LintedArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all().order_by('-date_published')
    serializer_class = serializers.LintedArticleSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('author__slug', 'source__slug')
    http_method_names = ['get']
    
class WorstLintedArticles(generics.ListCreateAPIView):
    queryset = Article.objects.annotate(Count('annotation')).order_by('-annotation__count')
    serializer_class = serializers.LintedArticleSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('author__slug', 'source__slug')
    http_method_names = ['get']
    
class AnnotationLabels(generics.ListCreateAPIView):   
    queryset = Annotation.objects.values('label','tag').annotate(count=Count('label')).order_by('-count') 
    serializer_class = serializers.CountedAnnotSerializer
    http_method_names = ['get']

class WorstAuthors(generics.ListCreateAPIView):   
    queryset = Author.objects.annotate(articles=Count('article')).annotate(
        count=Count('article__annotation')).order_by('-count') 
    serializer_class = serializers.RatedAuthorSerializer
    http_method_names = ['get']

#Article.objects.filter(annotation__label='born a (wom)an')
#a=Author.objects.filter(article__source__slug='the-sun').annotate(count=Count('article__annotation
#     ...: ')).order_by('-count')
 
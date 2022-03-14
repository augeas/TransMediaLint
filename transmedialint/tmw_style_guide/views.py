
from django.db.models import Count
from django.shortcuts import render
from django_filters import FilterSet
from rest_framework import generics
from rest_framework import status, viewsets

from sources.models import Article, Author
from tmw_style_guide.models import Annotation, RatedArticle
from tmw_style_guide import serializers


class RatedArticleFilter(FilterSet):
    class Meta:
        model = RatedArticle
        fields = ('article__slug', 'article__author__slug')


class RatedArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RatedArticle.objects.all().order_by('-offensive',
        '-inaccurate', '-inappropriate')
    serializer_class = serializers.RatedArticleSerializer
    filterset_class = RatedArticleFilter
    

'''
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


class AnnotationList(generics.ListCreateAPIView):
    queryset = Annotation.objects.all()
    serializer_class = serializers.AnnotSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('tag', 'article__slug', 'article__id')
    http_method_names = ['get']


class AuthorFilter(filters.FilterSet):
    source = filters.CharFilter(name='article__source__slug', lookup_expr='iexact')

    class Meta:
        model = Author
        fields = ('source',)


class WorstAuthors(generics.ListCreateAPIView):   
    queryset = Author.objects.annotate(articles=Count('article')).annotate(
        annots=Count('article__annotation')).order_by('-annots') 
    serializer_class = serializers.RatedAuthorSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('article__source__slug',)
    filter_class = AuthorFilter
    http_method_names = ['get']
 
'''

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render

from rest_framework import generics

from sources.models import Article

from . import serializers

class LintedArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = serializers.LintedArticleSerializer
    
class WorstLintedArticles(generics.ListCreateAPIView):
    queryset = Article.objects.annotate(Count('annotation')).order_by('-annotation__count')
    serializer_class = serializers.LintedArticleSerializer
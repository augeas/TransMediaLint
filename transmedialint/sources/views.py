
from django.shortcuts import render

from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.response import Response

from sources.crawlers import all_the_crawlers
from sources.models import Source
from sources import serializers


crawlers_by_slug = {crawler.crawler: crawler for crawler in all_the_crawlers}


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = serializers.SourceSerializer



class CrawlerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = all_the_crawlers
    serializer_class = serializers.CrawlerSerializer
    
    
    def retrieve(self, request, pk=None):
        crawler = crawlers_by_slug.get(pk)
        serializer = serializers.CrawlerSerializer(crawler)
        return Response(serializer.data) 

    
    @action(detail=True, methods=['get'])
    def crawl(self, request, pk=None):
        crawler = crawlers_by_slug.get(pk)
        if not crawler:
            return Response({"detail": "No such crawler."}, status=status.HTTP_404_NOT_FOUND)
        try:
            jobs = crawler.get_jobs()
        except:
            return Response({'error': 'crawler not deployed'})
        if any(map(jobs.get, ('pending', 'running'))):
            return Response({'error': 'crawler already running'})
        crawler.scrape()
        return Response({'crawler': pk, 'error': False}) 


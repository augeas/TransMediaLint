
from django.shortcuts import render
from rest_framework import status, viewsets

from tml_corpus.models import ArticleEntity, NamedEntity
from tml_corpus import serializers


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NamedEntity.objects.all()
    serializer_class = serializers.NamedEntitySerializer

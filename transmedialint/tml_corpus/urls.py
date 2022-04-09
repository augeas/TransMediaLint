
from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from tml_corpus import chart_views, views


router = DefaultRouter()
router.register(r'entities', views.EntityViewSet, basename='entity')

urlpatterns = router.urls

patterns = [
    re_path(r'^charts/source_entities$',chart_views.source_entity_chart),
    re_path(r'^charts/rated_entities$',chart_views.annotated_entity_chart)
]

urlpatterns = format_suffix_patterns(patterns)

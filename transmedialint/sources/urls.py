
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'sources', views.SourceViewSet, basename='source')
router.register(r'crawlers', views.CrawlerViewSet, basename='crawler')

urlpatterns = router.urls


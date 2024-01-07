from django.urls import re_path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from . import views, chart_views

router = DefaultRouter()

router.register('rated_articles', views.RatedArticleViewSet,
    basename='rated_article')

router.register('export_rated_articles', views.RatedArticleExportViewSet)

patterns = [
    re_path(r'^charts/rated_articles$', chart_views.rated_article_chart),
    re_path(r'^charts/annotations$', chart_views.annotation_label_chart),
    re_path(r'^charts/rated_authors$', chart_views.rated_author_chart),
]

urlpatterns = router.urls + format_suffix_patterns(patterns)






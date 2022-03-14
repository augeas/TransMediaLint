from django.urls import re_path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from . import views, chart_views

router = DefaultRouter()

router.register('rated_articles', views.RatedArticleViewSet,
    basename='rated_article')

#router.register('article_chart', chart_views.rated_article_chart,
#    basename='rated_article')

#urlpatterns = router.urls



patterns = [
#    re_path(r'^lintedarticles/$', views.LintedArticleList.as_view()),
#    re_path(r'^worstlintedarticles/$', views.WorstLintedArticles.as_view()),
#    re_path(r'^annotationlabels/$', views.AnnotationLabels.as_view()),
#    re_path(r'^annotations/$', views.AnnotationList.as_view()),
#    re_path(r'^worstauthors/$',views.WorstAuthors.as_view()),
    re_path(r'^charts/rated_articles$',chart_views.rated_article_chart),
]

urlpatterns = format_suffix_patterns(patterns)




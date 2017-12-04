from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views, chart_views

urlpatterns = [
    url(r'^lintedarticles/$', views.LintedArticleList.as_view()),
    url(r'^worstlintedarticles/$', views.WorstLintedArticles.as_view()),
    url(r'^annotationlabels/$', views.AnnotationLabels.as_view()),
    url(r'^annotations/$', views.AnnotationList.as_view()),
    url(r'^worstauthors/$',views.WorstAuthors.as_view()),
    url(r'^charts/rated_articles$',chart_views.rated_article_chart),
]

urlpatterns = format_suffix_patterns(urlpatterns)




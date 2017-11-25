from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^lintedarticles/$', views.LintedArticleList.as_view()),
    url(r'^worstlintedarticles/$', views.WorstLintedArticles.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)




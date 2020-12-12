

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from tml_corpus import views


router = DefaultRouter()
router.register(r'entities', views.EntityViewSet, basename='entity')

urlpatterns = router.urls

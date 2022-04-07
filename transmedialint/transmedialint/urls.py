"""transmedialint URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import re_path, path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns


from sources.urls import router as source_router
from tml_corpus.urls import router as corpus_router
from tml_corpus.urls import urlpatterns as corpus_urls

from tmw_style_guide.urls import router as style_guide_router
from tmw_style_guide.urls import urlpatterns as style_guide_urls


router = DefaultRouter()

router.registry.extend(source_router.registry)
router.registry.extend(style_guide_router.registry)
router.registry.extend(corpus_router.registry)

urlpatterns = [
    path('admin', admin.site.urls),
    path('api/', include(router.urls)),
] + style_guide_urls + corpus_urls

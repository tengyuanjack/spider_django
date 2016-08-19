"""spider_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'spider.views.index'),
    url(r'^index/', 'spider.views.index', name='index'),
    url(r'^handle1/', 'spider.views.handle1', name='handle1'),
    url(r'^handle2/', 'spider.views.handle2', name='handle2'),
    url(r'^handle3/', 'spider.views.handle3', name='handle3'),
    url(r'^handle4/', 'spider.views.handle4', name='handle4'),
    url(r'^handle5/', 'spider.views.handle5', name='handle5'),
    url(r'^handle6/', 'spider.views.handle6', name='handle6'),
    url(r'^handle7/', 'spider.views.handle7', name='handle7'),
    url(r'^handle8/', 'spider.views.handle8', name='handle8'),
    url(r'^handle9/', 'spider.views.handle9', name='handle9'),
    url(r'^sentiment/', 'spider.views.sentiment', name='sentiment'),
    url(r'^sentiment2/', 'spider.views.sentiment2', name='sentiment2'),
    url(r'^deleteCommentFile/', 'spider.views.deleteCommentFile', name='deleteCommentFile'),
    url(r'^deleteUserFile/', 'spider.views.deleteUserFile', name='deleteUserFile'),
    url(r'^deleteGlobalVar/', 'spider.views.deleteGlobalVar', name='deleteGlobalVar'),
    url(r'^test/', 'spider.views.test', name='test'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

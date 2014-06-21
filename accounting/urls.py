from django.conf.urls import patterns, url
from accounting import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^report/$', views.report, name='report'),
)

from django.conf.urls import patterns, url
from robot import views

urlpatterns = patterns('',
    url(r'^robot/validate/$', views.validate, name='validate'),
)

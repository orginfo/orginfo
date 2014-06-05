from django.conf.urls import patterns, url
from accounting import views

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounting/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login/'}),
    url(r'^organization_details/$', views.organization_details, name='organization_details'),
    url(r'^clients/$', views.clients, name='clients'),
    url(r'^$', views.index, name='index'),
)

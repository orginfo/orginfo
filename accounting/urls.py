from django.conf.urls import patterns, url
from accounting import views

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounting/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login/'}),
    url(r'^$', views.index, name='index'),
    url(r'^report/$', views.report, name='report'),
    url(r'^real_estates/search/$', views.search_real_estates, name='search_real_estates'),
    url(r'^real_estates/options/$', views.real_estates_as_options, name='real_estates_as_options'),
)

from django.conf.urls import patterns, url
from accounting import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounting/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login/'}),
    url(r'^$', views.index, name='index'),
    url(r'^report/$', views.report, name='report'),
    url(r'^real_estates/options/$', views.real_estates_as_options, name='real_estates_as_options'),
    url(r'^accounts/$', login_required(views.Accounts.as_view(), login_url="/login/"), name='accounts'),
    #url(r'^readings/$', views.readings, name='readings'),
    url(r'^create_reading/$', views.CounterReadingTab.as_view(), name='create_reading'),
    url(r'^readings/$', login_required(views.CounterReadingTab.as_view(), login_url="/login/"), name='readings'),
)

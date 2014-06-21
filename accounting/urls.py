from django.conf.urls import patterns, url
from accounting import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounting/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login/'}),
    url(r'^organization_details/$', views.organization_details, name='organization_details'),
    url(r'^clients/(?P<client_id>\d+)/payments/take/$', login_required(views.TakePayment.as_view(success_url="/")), name='take_payment'),
    url(r'^clients/$', login_required(views.Clients.as_view()), name='clients'),
    url(r'^clients/add/$', login_required(views.AddClient.as_view(success_url="/clients/")), name='add_client'),
    url(r'^$', views.index, name='index'),
    url(r'^report/$', views.report, name='report'),
)

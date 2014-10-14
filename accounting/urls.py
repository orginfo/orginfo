from django.conf.urls import patterns, url
from accounting import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounting/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login/'}),
    url(r'^organization_details/$', views.organization_details, name='organization_details'),
    url(r'^clients/(?P<client_id>\d+)/payments/take/$', login_required(views.TakePayment.as_view(success_url="/")), name='take_payment'),
    url(r'^clients/$', login_required(views.Clients.as_view()), name='clients'),
    url(r'^clients/add/$', login_required(views.CreateClient.as_view(success_url="/clients/")), name='add_client'),
    url(r'^clients/(?P<pk>\d+)/$', views.UpdateClient.as_view(success_url=""), name='client_update'),
    url(r'^$', views.index, name='index'),
    url(r'^report/$', views.report, name='report'),
    url(r'^robot/$', views.robot, name='robot'),
    url(r'^real_estates/$', views.RealEstates.as_view(), name='real_estates'),
    url(r'^real_estates/add/$', views.CreateRealEstate.as_view(success_url="/real_estates/"), name='add_real_estate'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/readings/$', views.ColdWaterReadings.as_view(), name='readings'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/readings/create/$', views.CreateColdWaterReading.as_view(), name='create_reading'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/readings/(?P<pk>\d+)/$', views.UpdateColdWaterReading.as_view(), name='update_reading'),
    url(r'^clients/(?P<pk>\d+)/services/$', views.ClientServices.as_view(), name='client_services'),
    url(r'^clients/(?P<pk>\d+)/services/create/$', views.CreateClientService.as_view(success_url=None), name='create_client_service'),
    url(r'^clients/(?P<client_id>\d+)/services/(?P<pk>\d+)/$', views.UpdateClientService.as_view(success_url=None), name='client_service'),
)

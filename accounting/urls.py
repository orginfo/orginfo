from django.conf.urls import patterns, url
from accounting import views
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounting/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/login/'}),
    url(r'^organization_details/$', views.organization_details, name='organization_details'),
    url(r'^$', views.index, name='index'),
    #url(r'^report/$', views.report, name='report'),
    url(r'^robot/$', views.robot, name='robot'),
    url(r'^real_estates/$', views.RealEstates.as_view(), name='real_estates'),
    url(r'^real_estates/create/$', views.CreateRealEstate.as_view(success_url="/real_estates/"), name='create_real_estate'),
    url(r'^real_estates/(?P<pk>\d+)/$', views.UpdateRealEstate.as_view(success_url=""), name='update_real_estate'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/readings/$', views.ColdWaterReadings.as_view(), name='readings'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/readings/create/$', views.CreateColdWaterReading.as_view(), name='create_reading'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/readings/(?P<pk>\d+)/$', views.UpdateColdWaterReading.as_view(), name='update_reading'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/service_usages/$', views.ServiceUsages.as_view(), name='service_usages'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/service_usage/create/$', views.CreateServiceUsage.as_view(), name='create_service_usage'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/service_usage/(?P<pk>\d+)/$', views.UpdateServiceUsage.as_view(success_url=None), name='service_usage'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/accounts/$', views.Accounts.as_view(), name='accounts'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/accounts/create/$', views.CreateAccount.as_view(), name='create_account'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/accounts/(?P<pk>\d+)/$', views.UpdateAccount.as_view(success_url=None), name='account'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/payments/$', views.Payments.as_view(), name='payments'),
    url(r'^real_estates/(?P<real_estate_id>\d+)/accounts/(?P<account_id>\d+)/payments/create/$', views.CreatePayment.as_view(), name='create_payment'),
)

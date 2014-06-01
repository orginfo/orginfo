from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'orginfo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include('accounting.urls', namespace="accounting")),
    url(r'^admin/', include(admin.site.urls)),
)

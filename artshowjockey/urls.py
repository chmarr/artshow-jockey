from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^artshow/', include('artshow.urls')),
    url(r'^peeps/', include('peeps.urls')),
    ('^$', redirect_to, {'url': '/artshow/'}),
)
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import redirect_to
from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^artshow/', include('artshow.urls')),
    url(r'^peeps/', include('peeps.urls')),
    ('^$', redirect_to, {'url': '/artshow/'}),
)
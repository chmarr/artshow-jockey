from django.conf.urls import patterns, include, url
from django.contrib import admin
from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^admin/lookups/', include(ajax_select_urls)),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^artshow/', include('artshow.urls')),
                       url(r'^manage/', include('artshow.manage_urls')),
                       url(r'^peeps/', include('peeps.urls')),
                       url(r'^accounts/', include('tinyreg.urls')),
                       url(r'^$', 'artshow.views.home', name="home"),
)
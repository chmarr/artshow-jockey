# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.conf.urls.defaults import *

urlpatterns = patterns('artshow',
	(r'^$', 'manage.index' ),
	(r'^artist/(?P<artist_id>\d+)/$', 'manage.artist' ),
	(r'^artist/(?P<artist_id>\d+)/pieces/$', 'manage.pieces' ),
	(r'^artist/(?P<artist_id>\d+)/downloadcsv/$', 'manage.downloadcsv' ),
)

# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.conf.urls import patterns, url

urlpatterns = patterns('artshow',
                       (r'^$', 'manage.index' ),
                       (r'^artist/(?P<artist_id>\d+)/$', 'manage.artist'),
                       (r'^artist/(?P<artist_id>\d+)/artist/$', 'manage.artist_details'),
                       (r'^artist/(?P<artist_id>\d+)/person/$', 'manage.person_details'),
                       (r'^artist/(?P<artist_id>\d+)/pieces/$', 'manage.pieces'),
                       (r'^artist/(?P<artist_id>\d+)/spaces/$', 'manage.spaces'),
                       (r'^artist/(?P<artist_id>\d+)/downloadcsv/$', 'manage.downloadcsv'),
                       (r'^artist/(?P<artist_id>\d+)/bidsheets/$', 'manage.bid_sheets'),
                       (r'^artist/(?P<artist_id>\d+)/controlforms/$', 'manage.control_forms'),
                       (r'^artist/(?P<artist_id>\d+)/makepayment/$', 'manage.make_payment'),
                       (r'^artist/(?P<artist_id>\d+)/makepayment/complete/email/$', 'manage.payment_made_email'),
                       (r'^artist/(?P<artist_id>\d+)/makepayment/complete/paypal/$', 'manage.payment_made_paypal'),
                       (r'^artist/(?P<artist_id>\d+)/makepayment/cancelled/paypal/$', 'manage.payment_cancelled_paypal'),
                       (r'^register/$', 'register.main'),
                       url(r'^ipn/$', 'paypal.ipn_handler'),
                       url(r'^announcement/$', 'announcement.index', name="view_announcements"),
                       (r'^announcement/(?P<announcement_id>\d+)/$', 'announcement.show'),
)

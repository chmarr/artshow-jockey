# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from .bidderreg import bidderreg_wizard_view


urlpatterns = patterns('artshow',
                       (r'^$', 'views.index'),
                       (r'^entry/$', 'views.dataentry'),
                       (r'^entry/bidders/$', 'addbidder.bulk_add'),
                       (r'^entry/bids/$', 'addbidder.bid_bulk_add'),
                       (r'^entry/auction_bids/(?P<adult>[yn])/$', 'voice_auction.auction_bids'),
                       (r'^entry/order_auction/(?P<adult>[yn])/$', 'voice_auction.order_auction'),
                       #(r'^entry/bids/location/(?P<location>[^/]+)/$', 'bidentry.add_bids'),
                       (r'^reports/$', 'reports.index'),
                       (r'^artist/(?P<artist_id>\d+)/mailinglabel/$', 'views.artist_mailing_label'),
                       (r'^artist/(?P<artist_id>\d+)/piecereport/$', 'reports.artist_piece_report'),
                       (r'^reports/artists/$', 'reports.artists'),
                       (r'^reports/winning-bidders/$', 'reports.winning_bidders'),
                       (r'^reports/artist-panel-report/$', 'reports.artist_panel_report'),
                       (r'^reports/panel-artist-report/$', 'reports.panel_artist_report'),
                       (r'^reports/artist-payment-report/$', 'reports.artist_payment_report'),
                       (r'^reports/show-summary/$', 'reports.show_summary'),
                       (r'^reports/voice-auction/$', 'reports.voice_auction'),
                       (r'^reports/sales-percentiles/$', 'reports.sales_percentiles'),
                       (r'^reports/allocations-waiting/$', 'reports.allocations_waiting'),
                       (r'^cashier/$', 'cashier.cashier'),
                       (r'^cashier/bidder/(?P<bidder_id>\d+)/$', 'cashier.cashier_bidder'),
                       (r'^cashier/bidder/(?P<bidder_id>\d+)/invoices/$', 'cashier.cashier_bidder_invoices'),
                       (r'^cashier/invoice/(?P<invoice_id>\d+)/$', 'cashier.cashier_invoice'),
                       (r'^cashier/invoice/(?P<invoice_id>\d+)/print/$', 'cashier.print_invoice'),
                       (r'^cashier/invoice/(?P<invoice_id>\d+)/pdf/$', 'pdfreports.pdf_invoice'),
                       (r'^cashier/invoice/(?P<invoice_id>\d+)/picklist/$', 'pdfreports.pdf_picklist'),
                       (r'^reports/winning-bidders-pdf/$', 'pdfreports.winning_bidders'),
                       (r'^reports/bid-entry-by-location-pdf/$', 'pdfreports.bid_entry_by_location'),
                       (r'^reports/bid-entry-by-location-pdf/$', 'pdfreports.bid_entry_by_location'),
                       (r'^reports/artists-csv/$', 'csvreports.artists'),
                       (r'^reports/pieces-csv/$', 'csvreports.pieces'),
                       (r'^reports/bidders-csv/$', 'csvreports.bidders'),
                       (r'^reports/payments-csv/$', 'csvreports.payments'),
                       (r'^reports/cheques-csv/$', 'csvreports.cheques'),
                       (r'^access/$', 'views.artist_self_access'),
                       url(r'^bidderreg/$', permission_required('artshow.is_artshow_kiosk')(bidderreg_wizard_view),
                           name="artshow-bidderreg-wizard"),
                       (r'^bidderreg/done/$', 'bidderreg.final'),
                       (r'^bidder/$', 'views.bidder_results'),
                       (r'^workflows/$', 'workflows.index'),
                       (r'^workflows/printing/$', 'workflows.printing'),
)

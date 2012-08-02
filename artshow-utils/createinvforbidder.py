#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import Bidder, BidderId, Invoice, InvoiceItem
import optparse, datetime
import decimal
import settings


def get_options ():
	parser = optparse.OptionParser ()
	parser.add_option ( "--test", default=False, action="store_true" )
	opts, args = parser.parse_args()
	opts.bidderid = args[0]
	return opts

def create_invoice ( bidderid_id, test=False ):

	now = datetime.datetime.now ()

	bidderid = BidderId.objects.get ( id=bidderid_id )
	bidder = bidderid.bidder
	print "Bidder is", unicode(bidder)

	pieces_to_add = []
	total = 0

	for b in bidder.top_bids():
		print b.piece.id, unicode(b), b.buy_now_bid and "BuyNow" or "", b.piece.status, b.piece.voice_auction and "Voice auction" or ""
		if b.piece.status == 2:
			print "adding"
			print
			pieces_to_add.append ( b.piece )
		else:
			print "NOT ADDING ***"
			print

	input = raw_input ( "Proceed?" )
	if input != "y":
		raise SystemExit

	if not test:
		items_to_add = []
		invoice = Invoice ( payer = bidder, paid_date=now )
		total = 0
		for p in pieces_to_add:
			top_bid = p.top_bid ()
			item = InvoiceItem ( piece=p, invoice=invoice, price=top_bid.amount )
			items_to_add.append ( item )
			total += top_bid.amount
		tax_rate = decimal.Decimal(settings.ARTSHOW_TAX_RATE)
		tax_paid = total * tax_rate
		total_incl_tax = total + tax_paid
		invoice.tax_paid = tax_paid
		invoice.total_paid = total_incl_tax
		invoice.save ()
		for i in items_to_add:
			i.invoice = invoice
			i.save ()
		for p in pieces_to_add:
			p.status = 3
			p.save ()

	print "Invoice Created:", invoice.id


if __name__ == "__main__":
	opts = get_options ()
	create_invoice ( opts.bidderid, test=opts.test )


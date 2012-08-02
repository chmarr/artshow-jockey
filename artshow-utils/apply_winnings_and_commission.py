#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import Artist, Payment, PaymentType, Bid
import datetime, decimal
import optparse
from settings import ARTSHOW_COMMISSION

def apply_winnings_and_commissions ( ids=None ):
	if ids:
		artists = Artist.objects.filter(id__in=ids)
	else:
		artists = Artist.objects.all()
	for a in artists:
		pt_winning = PaymentType.objects.get(name="Winnings")
		pt_commission = PaymentType.objects.get(name="Commission")
		total_winnings = 0
		total_pieces = 0
		pieces_with_bids = 0
		for piece in a.piece_set.all():
			if piece.status != 0:
				total_pieces += 1
			try:
				top_bid = piece.top_bid()
				total_winnings += top_bid.amount
				pieces_with_bids += 1
			except Bid.DoesNotExist:
				pass
		commission = total_winnings * decimal.Decimal(ARTSHOW_COMMISSION)

		if total_pieces > 0:
			payment = Payment ( artist=a, amount=total_winnings, payment_type=pt_winning, description="Sales (%d piece%s, %d with bid%s)" % ( total_pieces, total_pieces!=1 and "s" or "", pieces_with_bids, pieces_with_bids != 1 and "s" or ""), date=datetime.datetime.now() )
			payment.save ()

		if commission > 0:
			payment = Payment ( artist=a, amount=-commission, payment_type=pt_commission, description="10% Commission on sales", date=datetime.datetime.now() )
			payment.save ()

def get_options ():
	parser = optparse.OptionParser ()
	parser.add_option ( "--ids", type="str", default=None )
	opts, args = parser.parse_args ()
	if opts.ids:
		opts.ids = opts.ids.split(",")
		opts.ids = [int(x) for x in opts.ids]
	return opts

if __name__ == "__main__":
	opts = get_options ()
	apply_winnings_and_commissions ( opts.ids )

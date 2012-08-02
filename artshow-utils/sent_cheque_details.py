#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import Payment, PaymentType
import optparse, csv, sys

def sent_cheque_details ():
	csv_out = csv.writer ( sys.stdout )
	csv_out.writerow ( ( 'date', 'recipient', 'description', 'amount' ) )
	pt = PaymentType.objects.get ( name="Payment Sent" )
	for p in Payment.objects.filter ( payment_type=pt ).order_by ( 'date','artist' ):
		details = str(p.description).replace ( "Disbursement Cheque ","" )
		csv_out.writerow ( ( p.date, p.artist.chequename(), details, "$%.02f" % -p.amount ) )


def get_options ():
	parser = optparse.OptionParser ()
	opts, args = parser.parse_args ()
	return opts

def main ():
	opts = get_options ()
	sent_cheque_details ()

if __name__ == "__main__":
	main ()
	


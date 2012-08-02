#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import Artist, Payment, PaymentType
import optparse, decimal, csv, datetime

def integrate_cheques ( csv_file ):
	c = csv.DictReader(open(csv_file))

	pt =  PaymentType.objects.get(name='Payment Sent')

	for row in c:
		try:
			artistid = row['artist']
			chq = row['chq']
			amount = decimal.Decimal(row['amount'])
		except:
			print >>sys.stderr, "bad row:", row
			continue
		try:
			artist = Artist.objects.get(artistid=artistid)
		except Artist.DoesNotExist:
			print >>sys.stderr, "artist %d not found"
			continue

		payment = Payment(artist=artist, amount=-amount, payment_type=pt, description="Disbursement Cheque #"+chq, date=datetime.datetime.now() )
		payment.save ()


def get_options ():
	parser = optparse.OptionParser ()
	opts, args = parser.parse_args()
	opts.infile = args[0]
	return opts


def main ():
	opts = get_options ()
	integrate_cheques ( opts.infile )

if __name__ == "__main__":
	main ()

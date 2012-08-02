#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

import sys
sys.path.append ( "/home/chris/dev/artshowproj" )
sys.path.append ( "/home/chris/dev" )

from artshow import invoicegen
from artshow.models import Invoice
import optparse

def print_invoices ( invoices, copy_name ):
	for invoice_id in invoices:
		invoice = Invoice.objects.get(id=invoice_id)
		invoicegen.print_invoice ( invoice, copy_name )
	
def get_options ():
	parser = optparse.OptionParser ()
	opts, args = parser.parse_args ()
	opts.invoices = [ int(x) for x in args ]
	return opts
	
def main ():
	opts = get_options ()
	for c in [ "CUSTOMER COPY", "MERCHANT COPY", "PICK LIST" ]:
		print_invoices ( opts.invoices, c )
	
if __name__ == "__main__":
	main ()
	
	

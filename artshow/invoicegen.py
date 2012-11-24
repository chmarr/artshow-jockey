#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from models import Invoice
import sys, subprocess
from django.conf import settings
from logging import getLogger
from StringIO import StringIO
logger = getLogger(__name__)

invoice_header = """\
+------------------------------------------------------------------------------+
|                                                                              |
|  %(showstr)-30s   DATE: %(datestr)-14s  INVOICE: %(invoice)-10s  |
|                                                                              |
|  FOR: %(name)-48s  PAGE: %(pageno)-3d of %(numpages)-3d     |
|  (BIDDER ID: %(bidderidstr)-s) %(bidderidpad)s                        |
|                                                                              |
+------------------------------------------------------------------------------+
|                                                                              |
|  ITEM                                                         AMOUNT         |
|                                                                              |
"""

invoice_lines = """\
|  %(itemstr)-59s  %(amtstr)9s      |
"""

invoice_spacer = """\
|                                                                              |
"""

non_last_invoice_footer = """\
|                                                                              |
|                                                                              |
|                                                                              |
|                                                                              |
+------------------------------------------------------------------------------+

          %(copystr)60s          
\x0c"""

last_invoice_footer = """\
|                              %(taxdescstr)30s   %(taxamtstr)9s      |
|                                                              -----------     |
|  ITEM COUNT: %(itemcount)-4d                                     TOTAL   %(totalstr)9s      |
|                                                                              |
+------------------------------------------------------------------------------+

          %(copystr)60s          
"""


def wrap_str ( s, cols ):
	new_lines = []
	while len(s) > cols:
		pos = s.rfind(" ",0,cols)
		if pos == -1:
			pos = s.find(" ",cols)
		if pos == -1:
			break
		new_lines.append ( s[:pos].rstrip() )
		s = s[pos:].lstrip()
	new_lines.append ( s )
	return new_lines



def print_invoice ( invoice, copy_name="SINGLE COPY", dest=sys.stdout ):
	pageno = 1
	numpages = 2
	bidderidstr = ", ".join([x.id for x in invoice.payer.bidderid_set.all()])
	bidderidpad = " " * ( 38 - len(bidderidstr) )
	taxdescstr = settings.ARTSHOW_TAX_DESCRIPTION
	
	invoiceitems = invoice.invoiceitem_set.all().order_by ( 'piece__location', 'piece' )
	
	invoice_page = 1
	lines_this_page = 0
	max_lines_per_page = 48

	for invoiceitem in invoiceitems:
		piece = invoiceitem.piece
		piece.name_wrapped = wrap_str(str(piece) + "  @ %s" % piece.location ,59)
		num_lines = len(piece.name_wrapped)
		if lines_this_page + num_lines + 1 > max_lines_per_page:
			invoice_page += 1
			lines_this_page = 0
		invoiceitem.invoice_page = invoice_page
		lines_this_page += num_lines + 1
		
	numpages = invoice_page
	numitems = len(invoiceitems)

	invoice_page = 1
	invoice_idx = 0
	
	while invoice_idx < numitems:

		lines_this_page = 0
		dest.write ( invoice_header % { 
				'showstr': settings.ARTSHOW_SHOW_NAME.upper(),
				'datestr': str(invoice.paid_date),
				'invoice': settings.ARTSHOW_INVOICE_PREFIX + str(invoice.id),
				'name': str(invoice.payer.name()),
				'pageno': pageno,
				'numpages': numpages,
				'bidderidstr': bidderidstr,
				'bidderidpad': bidderidpad,
				} )
				
		while invoice_idx < numitems and invoice_page==invoiceitems[invoice_idx].invoice_page:
			invoiceitem = invoiceitems[invoice_idx]
			piece = invoiceitem.piece
			for l in piece.name_wrapped[:-1]:
				dest.write (invoice_lines % { 'itemstr':l, 'amtstr': "" })
			dest.write (invoice_lines % { 'itemstr':piece.name_wrapped[-1], 'amtstr': "$%8.2f" % invoiceitem.price })
			dest.write (invoice_spacer)
			lines_this_page += len(piece.name_wrapped) + 1
			invoice_idx += 1
			
		for i in range ( lines_this_page, max_lines_per_page ):
			dest.write ( invoice_spacer )
			
		if invoice_page == numpages:
			dest.write ( last_invoice_footer % { 'taxdescstr':taxdescstr,
					'taxamtstr': "$%8.2f" % invoice.tax_paid,
					'totalstr': "$%8.2f" % invoice.total_paid(),
					'copystr': copy_name.center(60),
					'itemcount': numitems,
					} )
		else:
			dest.write ( non_last_invoice_footer % { 'copystr': copy_name.center(60) } )
			
		invoice_page += 1

class PrintingError ( StandardError ):
	pass
	
def print_invoices ( invoices, copy_names, to_printer=False ):

	sbuf = StringIO()
	
	for invoice_id in invoices:
		try:
			invoice = Invoice.objects.get(id=invoice_id)
		except Invoice.DoesNotExist:
			logger.error ( "Invoice %s does not exist", invoice_id )
		else:
			if copy_names:
				for copy_name in copy_names:
					print_invoice ( invoice, copy_name, dest=sbuf )
			else:
				print_invoice ( invoice, "", dest=sbuf )
			
	if not sbuf.getvalue():
		logger.error ( "nothing to generate" )
	elif to_printer:
		p = subprocess.Popen ( settings.ARTSHOW_PRINT_COMMAND, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True )
		output, error = p.communicate ( sbuf.getvalue() )
		if output:
			logger.debug ( "printing command returned: %s", output )
		if error:
			logger.error ( "printing command returned error: %s", error )
			raise PrintingError ( error )
	else:
		sys.stdout.write ( sbuf.getvalue() )

#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from models import Invoice
import sys
import subprocess
from django.conf import settings
from default_settings import _DISABLED as SETTING_DISABLED
from StringIO import StringIO
import re
from logging import getLogger
logger = getLogger(__name__)

invoice_header = """\
+------------------------------------------------------------------------------+
|                                                                              |
|  %(showstr)-30s   DATE: %(datestr)-14s  INVOICE: %(invoice)-10s  |
|                                                                              |
|  FOR: %(name)-48s  PAGE: %(pageno)-3d of MMM     |
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

tax_and_total_line = """\
|                              %(taxdescstr)30s   %(taxamtstr)9s      |
|                                                              -----------     |
|  ITEM COUNT: %(itemcount)-4d                                     TOTAL   %(totalstr)9s      |
"""

payment_line = """\
|     %(paymentdescstr)55s   %(paymentamtstr)9s      |
"""

invoice_footer = """\
+------------------------------------------------------------------------------+

          %(copystr)60s          
\x0c"""



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
	invoicepayments = invoice.invoicepayment_set.all()
	
	numitems = len(invoiceitems)

	buffer = StringIO()

	max_lines_per_page = 52
	invoice_page = 1
	lines_this_page = 0

	def write_header ():
		buffer.write ( invoice_header % { 
				'showstr': settings.ARTSHOW_SHOW_NAME.upper(),
				'datestr': str(invoice.paid_date),
				'invoice': settings.ARTSHOW_INVOICE_PREFIX + str(invoice.id),
				'name': str(invoice.payer.name()),
				'pageno': pageno,
				'numpages': numpages,
				'bidderidstr': bidderidstr,
				'bidderidpad': bidderidpad,
				} )
				
	def write_footer ():
		for i in range( max_lines_per_page - lines_this_page ):
			buffer.write (invoice_spacer)				
		buffer.write ( invoice_footer % { 'copystr': copy_name.center(60) } )
		
	def write_item ( name_wrapped, price ):
		for l in name_wrapped[:-1]:
			buffer.write (invoice_lines % { 'itemstr':l, 'amtstr': "" })
		buffer.write (invoice_lines % { 'itemstr':name_wrapped[-1], 'amtstr': "$%8.2f" % price })
		buffer.write (invoice_spacer)				
		
	def write_payment ( payment ):
		payment_description = 'Paid %s' % payment.get_payment_method_display()
		if payment.notes:
			payment_description += ": " + payment.notes
		payment_description = payment_description[:55]
		buffer.write ( payment_line % { 'paymentdescstr': payment_description, 'paymentamtstr': "$%8.2f" % payment.amount } )

	write_header ()
	
	for item in invoiceitems:
		name_wrapped = wrap_str( str(item.piece) + "  @ %s" % item.piece.location, 59 )
		num_lines = len(name_wrapped)
		if lines_this_page + num_lines + 1 > max_lines_per_page:
			write_footer ()
			invoice_page += 1
			lines_this_page = 0
			write_header ()
		write_item ( name_wrapped, item.price )
		lines_this_page += num_lines + 1

	if lines_this_page + 5 > max_lines_per_page:
		write_footer ()
		invoice_page += 1
		lines_this_page = 0
		write_header ()
	buffer.write ( tax_and_total_line % { 'taxdescstr':taxdescstr,
			'taxamtstr': "$%8.2f" % invoice.tax_paid,
			'totalstr': "$%8.2f" % invoice.total_paid(),
			'copystr': copy_name.center(60),
			'itemcount': numitems,
			} )
	buffer.write (invoice_spacer)
	buffer.write (invoice_spacer)
	lines_this_page += 5
	
	for payment in invoicepayments:
		if lines_this_page + 1 > max_lines_per_page:
			write_footer ()
			invoice_page += 1
			lines_this_page = 0
			write_header ()
		write_payment ( payment )
		lines_this_page += 1
		
	write_footer ()
	
	s = buffer.getvalue ()
	s = re.sub ( "(?<= of )MMM", "%-3d"%invoice_page, s )
	
	dest.write ( s )


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
		if settings.ARTSHOW_PRINT_COMMAND is SETTING_DISABLED:
			logger.error ( "Cannot print invoice. ARTSHOW_PRINT_COMMAND is DISABLED" )
			raise PrintingError ( "Printing is DISABLED in configuration" )
		p = subprocess.Popen ( settings.ARTSHOW_PRINT_COMMAND, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True )
		output, error = p.communicate ( sbuf.getvalue() )
		if output:
			logger.debug ( "printing command returned: %s", output )
		if error:
			logger.error ( "printing command returned error: %s", error )
			raise PrintingError ( error )
	else:
		sys.stdout.write ( sbuf.getvalue() )

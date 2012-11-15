# Artshow Jockey
# Copyright (C) 2009, 2010, 2011 Chris Cogdon
# See file COPYING for licence details

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from artshow.models import Bidder, Piece, InvoicePayment, InvoiceItem, Bid, Invoice
from django import forms
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.forms import ModelForm, HiddenInput
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import modelformset_factory
from django.template import RequestContext
from django.conf import settings
import logging, datetime
logger = logging.getLogger ( __name__ )
import subprocess

class BidderSearchForm ( forms.Form ):
	text = forms.CharField ()
	
def cashier ( request ):
	if request.method == "POST":
		form = BidderSearchForm ( request.POST )
		if form.is_valid ():
			text = form.cleaned_data['text']
			# TODO - the following will return multiple entries for name base if bidder has two IDs
			bidders = Bidder.objects.filter ( Q(name__icontains=text) | Q(bidderid__id=text) )
		else:
			bidders = []
	else:
		form = BidderSearchForm ()
		bidders = []
		
	c = { "form":form, "bidders":bidders }
	c.update(csrf(request))
	return render_to_response ( 'artshow/cashier.html', c )
	
class TaxPaidForm ( forms.Form ):
	tax_paid = forms.DecimalField ()
	
class PaymentForm ( ModelForm ):
	class Meta:
		model = InvoicePayment
		fields=("amount","payment_method","notes")
		widgets={'amount':forms.HiddenInput,'payment_method':forms.HiddenInput,'notes':forms.HiddenInput}

PaymentFormSet = modelformset_factory ( InvoicePayment, form=PaymentForm, extra=0 )
	
class SelectPieceForm ( forms.Form ):
	select = forms.BooleanField ( required=False )
	
#TODO probably need a @transaction.commit_on_success here
	
def cashier_bidder ( request, bidder_id ):

	bidder = get_object_or_404 ( Bidder, pk=bidder_id )
	
	all_bids = bidder.top_bids( unsold_only=True )
	available_bids = []
	pending_bids = []
	bid_dict = {}
	for bid in all_bids:
		if bid.piece.status == Piece.StatusWon:
			available_bids.append ( bid )
			bid_dict[bid.pk] = bid
		else:
			pending_bids.append ( bid )

	if request.method == "POST":
		for bid in available_bids:
			form = SelectPieceForm ( request.POST, prefix="bid-%d"%bid.pk )
			bid.form = form
		tax_form = TaxPaidForm ( request.POST, prefix="tax" )
		payment_formset = PaymentFormSet ( request.POST, prefix="payment", queryset=InvoicePayment.objects.none() )
		if all( bid.form.is_valid() for bid in available_bids ) and tax_form.is_valid() and payment_formset.is_valid():
			logger.debug ( "Holy crap, everything passed" )
			tax_paid = tax_form.cleaned_data['tax_paid']
			### TODO verify that total items matches total paid
			invoice = Invoice ( payer=bidder, tax_paid=tax_form.cleaned_data['tax_paid'], paid_date=datetime.datetime.now() )
			invoice.save ()
			payments = payment_formset.save(commit=False)
			for payment in payments:
				payment.invoice = invoice
				payment.save ()
			for bid in available_bids:
				if bid.form.cleaned_data['select']:
					invoice_item = InvoiceItem ( piece=bid.piece, price=bid.amount, invoice=invoice )
					invoice_item.save ()
					bid.piece.status = Piece.StatusSold
					bid.piece.save ()
			p = subprocess.Popen ( ["/home/chris/dev/artshowproj/artshow-utils/igen", str(invoice.id)], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
			output, error = p.communicate ()
			logger.debug ( "printer returned: %s", output )
			if error:
				logger.error ( "printer error returned: %s", error )
			return redirect ( cashier_invoice, invoice_id=invoice.id )
	else:
		for bid in available_bids:
			form = SelectPieceForm ( prefix="bid-%d"%bid.pk, initial={"select":False} )
			bid.form = form
		tax_form = TaxPaidForm ( prefix="tax" )
		payment_formset = PaymentFormSet ( prefix="payment", queryset=InvoicePayment.objects.none() )
		
	payment_types = [ {'id':x[0],'name':x[1]} for x in InvoicePayment.PAYMENT_METHOD_CHOICES[1:] ]
	tax_rate = settings.ARTSHOW_TAX_RATE
	money_precision = settings.ARTSHOW_MONEY_PRECISION
		
	c = dict ( bidder=bidder, available_bids=available_bids, pending_bids=pending_bids, tax_form=tax_form, payment_formset=payment_formset, payment_types=payment_types,
			tax_rate=tax_rate, money_precision=money_precision )
	# c.update ( csrf(request) )
	return render_to_response ( 'artshow/cashier_bidder.html', c, context_instance=RequestContext(request) )
	
# TODO... show a mock-up of the invoice here.
	
def cashier_invoice ( request, invoice_id ):
	invoice = get_object_or_404 ( Invoice, pk=invoice_id )
	c = dict ( invoice=invoice )
	# c.update ( csrf(request) )
	return render_to_response ( 'artshow/cashier_invoice.html', c, context_instance=RequestContext(request) )
	
	

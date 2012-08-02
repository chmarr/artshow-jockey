# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from artshow.models import Bidder, BidderId
from django import forms
from django.core.context_processors import csrf
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError
import mod11codes

bidders_per_page = 10

def mod11check ( value ):
	try:
		mod11codes.check ( value )
	except mod11codes.CheckDigitError:
		raise ValidationError ( "Not a valid code" )


class BidderAddForm ( forms.Form ):
	bidderid = forms.CharField ( required=False, max_length=8, validators=[mod11check] )
	name = forms.CharField ( required=False, max_length=100 )
	regid = forms.CharField ( required=False, max_length=10 )
	def clean ( self ):
		super(BidderAddForm,self).clean()
		cleaned_data = self.cleaned_data
		if ( cleaned_data.get('bidderid') or cleaned_data.get('name') or cleaned_data.get('regid') ):
			msg = u"This field is required"
			if cleaned_data.get('bidderid') == "":
				self._errors['bidderid'] = ErrorList([msg])
				del cleaned_data['bidderid']
			if cleaned_data.get('name') == "":
				self._errors['name'] = ErrorList([msg])
				del cleaned_data['name']
			if cleaned_data.get('regid') == "":
				self._errors['regid'] = ErrorList([msg])
				del cleaned_data['regid']
		return cleaned_data


def bulk_add ( request ):
	if request.method == "POST":
		forms = [ BidderAddForm ( request.POST, prefix=str(i) ) for i in range(bidders_per_page) ]
		all_valid=True
		for form in forms:
			if not form.is_valid():
				all_valid=False
		if all_valid:
			for form in forms:
				bidderid = form.cleaned_data.get('bidderid')
				if not bidderid: continue
				name = form.cleaned_data['name']
				regid = form.cleaned_data['regid']
				bidder = Bidder ( name=name, regid=regid )
				bidder.save ()
				bidderid = BidderId ( id=bidderid, bidder=bidder )
				bidderid.save ()
			return HttpResponseRedirect('.')
	else:
		forms = [ BidderAddForm ( prefix=str(i) ) for i in range(bidders_per_page) ]
	c = {'forms':forms}
	c.update(csrf(request))
	return render_to_response ( 'artshow/bidderbulkadd.html', c )
	

def single_add ( request ):
	if request.method == 'POST':
		form = BidderBulkAddForm ( request.POST )
		if form.is_valid ():
			bidderid = form.cleaned_data['bidderid']
			name = form.cleaned_data['name']
			regid = form.cleaned_data['regid']
			bidder = Bidder ( name=name, bidderid=bidderid, regid=regid )
			bidder.save ()
			return HttpResponseRedirect('.')
	else:
		form = BidderBulkAddForm ()
	c = {'form': form}
	c.update(csrf(request))
	return render_to_response ( 'artshow/bidderadd.html', c )

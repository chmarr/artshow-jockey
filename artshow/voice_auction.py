from artshow.models import Piece, Bid, BidderId
from django import forms
from django.forms.models import modelformset_factory, formset_factory
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
from logging import getLogger
from django.core.exceptions import ValidationError

logger=getLogger(__name__)

class AuctionOrderingForm ( forms.ModelForm ):
	class Meta:
		model = Piece
		fields = ( "order", )
		
AuctionOrderingFormSet = modelformset_factory ( Piece, form=AuctionOrderingForm, extra=0 )
		
		
@permission_required ( 'artshow.add_piece' )
def order_auction ( request, adult ):

	adult = adult == "y"

	pieces = Piece.objects.filter ( voice_auction=True, adult=adult ).order_by ( 'order', 'artist', 'pieceid' )
	
	if request.method == "POST":
		formset = AuctionOrderingFormSet ( request.POST, queryset=pieces )
		if formset.is_valid ():
			formset.save ()
			messages.info ( request, "Auction Ordering Saved" )
			return redirect ( "." )
	else:
		formset = AuctionOrderingFormSet ( queryset=pieces )
				
	return render ( request, "artshow/order_auction.html", {'formset':formset, 'adult':adult} )



class AuctionBidForm ( forms.Form ):

	ACTION_CHOICES = (
		( 0, "Defer" ),
		( 1, "To Bid Sheet" ),
		( 2, "Outbid" ),
		)
		
	piece = forms.ModelChoiceField ( queryset=Piece.objects.filter(status=Piece.StatusInShow), widget=forms.HiddenInput )
	action = forms.ChoiceField ( choices=ACTION_CHOICES, initial=0, widget=forms.RadioSelect )
	bidder = forms.ModelChoiceField ( queryset=BidderId.objects.all(), widget=forms.TextInput, required=False )
	amount = forms.IntegerField ( required=False )
	
	def clean_action ( self ):
		action = self.cleaned_data['action']
		return int(action)
	
						
	def clean ( self ):
		cleaned_data = super(AuctionBidForm, self).clean()
		action = cleaned_data['action']
		bidder = cleaned_data.get('bidder',None)
		amount = cleaned_data.get('amount',None)
		msg1 = "This field required if action is \"Outbid\""
		msg2 = "This field must be empty if action is \"Defer\" or \"To Bid Sheet\""
		if action==2:
			if bidder is not None and not bidder:
				self._errors['bidder'] = self.error_class([msg1])
			if not amount:
				self._errors['amount'] = self.error_class([msg1])
		else:
			if bidder:
				self._errors['bidder'] = self.error_class([msg2])
				del cleaned_data['bidder']
			if amount:
				self._errors['amount'] = self.error_class([msg2])
				del cleaned_data['amount']
		return cleaned_data
		

		
AuctionBidFormSet = formset_factory ( AuctionBidForm, extra=0 )


def auction_bids ( request, adult ):

	adult = adult=="y"
	pieces = Piece.objects.filter ( voice_auction=True, status=Piece.StatusInShow, adult=adult ).order_by ( "order", "artist", "pieceid" )
	
	initial_data = [ {'piece':p} for p in pieces ]
	
	if request.method == "POST":
		formset = AuctionBidFormSet ( request.POST, initial=initial_data )
		if formset.is_valid ():
			for form in formset:
				piece = form.cleaned_data['piece']
				action = form.cleaned_data['action']
				bidder = form.cleaned_data['bidder']
				amount = form.cleaned_data['amount']
				if action == 1:
					try:
						top_bid = piece.top_bid()
						if piece.status == piece.StatusInShow:
							piece.status = piece.StatusWon
							piece.save()
							messages.info ( request, "%s marked won to bid sheet" % piece )
						else:
							messages.error ( request, "%s not marked as status is not \"In Show\"" % piece )
					except Bid.DoesNotExist:
						pass
				elif action == 2:
					b = Bid ( bidder=bidder.bidder, amount=amount, piece=piece )
					try:
						b.validate()
					except ValidationError, x:
						messages.error ( request, "Bid on %s not saved: %s" % ( piece, x ) )
					else:
						b.save ()
						piece.status = piece.StatusWon
						piece.save ()
						messages.info ( request, "Bid on %s saved" % piece )
			return redirect ( '.' )
	else:
		formset = AuctionBidFormSet ( initial=initial_data )
		
	return render ( request, "artshow/auction_bids.html", { 'formset':formset, 'adult':adult } )
	
	




from artshow.models import Piece, Bid
from django import forms
from django.forms.models import modelformset_factory, formset_factory
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
from logging import getLogger

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
		
	logger.debug ( "%s", dir(formset[0]) )
			
		
	return render ( request, "artshow/order_auction.html", {'formset':formset, 'adult':adult} )



class AuctionBidForm ( forms.ModelForm ):

	ACTION_CHOICES = (
		( 0, "Defer" ),
		( 1, "To Bid Sheet" ),
		( 2, "Outbid" ),
		)
		
	action = forms.ChoiceField ( choices=ACTION_CHOICES, initial=0, widget=forms.RadioSelect )

	class Meta:
		model = Bid
		fields = ( "action", "piece", "bidder", "amount" )
		widgets = {
			'bidder': forms.TextInput,
			'piece': forms.HiddenInput,
		}

		
AuctionBidFormSet = formset_factory ( AuctionBidForm, extra=0 )


def auction_bids ( request, adult ):

	adult = adult=="y"
	pieces = Piece.objects.filter ( voice_auction=True, adult=adult ).order_by ( "order", "artist", "pieceid" )
	
	initial_data = [ {'piece':p} for p in pieces ]
	logger.debug ( "initial_data %s", initial_data )
	
	if request.method == "POST":
		pass
	else:
		formset = AuctionBidFormSet ( initial=initial_data )
		
	for index, f in enumerate(formset):
		logger.debug ( "form %d %s", index, dir(f) )
				
	return render ( request, "artshow/auction_bids.html", { 'formset':formset, 'adult':adult } )
	
	




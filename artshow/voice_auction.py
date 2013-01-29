from artshow.models import Piece
from django import forms
from django.forms.models import modelformset_factory
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

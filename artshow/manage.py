from django.shortcuts import render, redirect, get_object_or_404
from artshow.models import *
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory, inlineformset_factory
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
import utils
import csv
import re

EXTRA_PIECES = 5

@login_required
def index ( request ):
	artists = Artist.objects.viewable_by ( request.user )
	return render ( request, "artshow/manage_index.html", {'artists':artists} )
	

@login_required	
def artist ( request, artist_id ):
	artist = get_object_or_404 ( Artist.objects.viewable_by(request.user), pk=artist_id )
	can_edit = artist.editable_by(request.user)
	return render ( request, "artshow/manage_artist.html", {'artist':artist,'can_edit':can_edit} )
	
class PieceForm ( forms.ModelForm ):
	class Meta:
		model = Piece
		fields=('pieceid','name','media','not_for_sale','adult','min_bid','buy_now')
		widgets={
			'pieceid': forms.TextInput ( attrs={'size':4} ),
			'name': forms.TextInput ( attrs={'size':40} ),
			'media': forms.TextInput ( attrs={'size':40} ),
			'min_bid': forms.TextInput ( attrs={'size':5} ),
			'buy_now': forms.TextInput ( attrs={'size':5} ),
		}
		
PieceFormSet = inlineformset_factory ( Artist, Piece, form=PieceForm, 
		extra=EXTRA_PIECES,
		can_delete=True,
		)

@login_required
def pieces ( request, artist_id ):

	artist = get_object_or_404 ( Artist.objects.viewable_by(request.user), pk=artist_id )
	
	if not artist.editable_by ( request.user ):
		return render ( request, "artshow/manage_pieces_noedit.html", {'artist':artist} )
	
	pieces = artist.piece_set.order_by ( "pieceid" )

	if request.method == "POST":
		formset = PieceFormSet ( request.POST, queryset=pieces, instance=artist )
		if formset.is_valid ():
			formset.save ()
			messages.info ( request, "Changes to piece details have been saved" )
			if request.POST.get('saveandcontinue'):
				return redirect ( '.' )
			else:
				return redirect ( reverse('artshow.manage.artist', args=(artist_id,)) )
	else:
		formset = PieceFormSet ( queryset=pieces, instance=artist )
		
	return render ( request, "artshow/manage_pieces.html", {'artist':artist,'formset':formset} )
	
def yesno ( b ):
	return "yes" if b else "no"
	
@login_required
def downloadcsv ( request, artist_id ):

	artist = get_object_or_404 ( Artist.objects.viewable_by(request.user), pk=artist_id )

	reduced_artist_name = re.sub ( '[^A-Za-z0-9]+', '', artist.artistname() ).lower()
	filename = "pieces-" + reduced_artist_name + ".csv"
	
	field_names = [ 'pieceid', 'code', 'title', 'media', 'min_bid', 'buy_now', 'adult', 'not_for_sale' ]
	
	response = HttpResponse ( mimetype="text/csv" )
	response['Content-Disposition'] = "attachment; filename=" + filename
	
	c = utils.UnicodeCSVWriter ( response )
	c.writerow ( field_names )

	for p in artist.piece_set.all():
		c.writerow ( ( p.pieceid, p.code, p.name, p.media, p.min_bid, p.buy_now, yesno(p.adult), yesno(p.not_for_sale) ) )
			
	return response	

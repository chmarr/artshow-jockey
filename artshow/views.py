# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.shortcuts import render_to_response
from django.http import HttpResponse
from artshow.models import Artist

def index ( request ):
	return render_to_response ( 'artshow/index.html' )
	
def dataentry ( request ):
	return render_to_response ( 'artshow/dataentry.html' )

def artist_mailing_label ( request, artist_id ):
	artist = Artist.objects.get(pk=artist_id)
	return render_to_response ( 'artshow/artist-mailing-label.html', { 'artist':artist } )

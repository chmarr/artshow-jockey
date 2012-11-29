# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.shortcuts import render, redirect
from artshow.models import Artist
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def home ( request ):
	if request.user.has_module_perms('artshow'):
		return redirect ( index )
	else:
		return redirect ( 'artshow.manage.index' )


@permission_required ( 'artshow.is_artshow_staff' )
def index ( request ):
	return render ( request, 'artshow/index.html' )
	
@permission_required ( 'artshow.is_artshow_staff' )
def dataentry ( request ):
	return render ( request, 'artshow/dataentry.html' )

@permission_required ( 'artshow.is_artshow_staff' )
def artist_mailing_label ( request, artist_id ):
	artist = Artist.objects.get(pk=artist_id)
	return render ( request, 'artshow/artist-mailing-label.html', { 'artist':artist } )

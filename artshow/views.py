# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details
from django.contrib import messages, auth
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelChoiceField, forms, CharField
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from .models import Artist, BidderId


def home(request):
    if request.user.has_module_perms('artshow'):
        return redirect(index)
    elif request.user.is_authenticated():
        return redirect('artshow.manage.index')
    else:
        return render(request, "artshow/home.html")


@permission_required('artshow.is_artshow_staff')
def index(request):
    return render(request, 'artshow/index.html')


@permission_required('artshow.is_artshow_staff')
def dataentry(request):
    return render(request, 'artshow/dataentry.html')


@permission_required('artshow.is_artshow_staff')
def artist_mailing_label(request, artist_id):
    artist = Artist.objects.get(pk=artist_id)
    return render(request, 'artshow/artist-mailing-label.html', {'artist': artist})


class SelectArtistForm(forms.Form):
    artist = ModelChoiceField(queryset=Artist.objects.all())


@permission_required('artshow.is_artshow_staff')
def artist_self_access(request):

    if request.method == "POST":
        form = SelectArtistForm(request.POST)
        if form.is_valid():
            artist = form.cleaned_data['artist']
            user = artist.person.user
            if user is None:
                messages.error(request, "The selected artist does not have a login created.")
            else:
                # TODO. Find a way to attach the correct backend for the artist.
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
                return redirect('/')
    else:
        form = SelectArtistForm()

    return render(request, "artshow/artist_self_access.html", {'form': form})


class BidderResultsForm(forms.Form):
    bidder_id = CharField(label="Bidder ID", required=True)
    reg_id = CharField(label="Registration ID", required=True)

    def clean(self):
        cleaned_data = super(BidderResultsForm, self).clean()
        if cleaned_data.get('bidder_id') and cleaned_data.get('reg_id'):
            try:
                bidderid = BidderId.objects.get(id=cleaned_data['bidder_id'])
                bidder = bidderid.bidder
                reg_id = bidder.person.reg_id
                assert reg_id == cleaned_data['reg_id']
            except (AssertionError, ObjectDoesNotExist):
                raise forms.ValidationError("Bidder or Registration ID is invalid.")
            cleaned_data['bidder'] = bidder
        return cleaned_data


@csrf_exempt
def bidder_results(request):

    # TODO set up gating controls for "bid information not ready" and "voice auction results not in"

    bidder = None
    if len(request.GET) > 0:
        form = BidderResultsForm(request.GET)
        if form.is_valid():
            bidder = form.cleaned_data['bidder']
    else:
        form = BidderResultsForm()

    return render(request, "artshow/bidder_results.html", {'form': form, 'bidder': bidder})



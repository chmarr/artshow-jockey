# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.shortcuts import render, redirect
from artshow.models import Bidder, BidderId, Person, Piece
from django import forms
from django.core.exceptions import ValidationError
import mod11codes
import re
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import permission_required

BIDDERS_PER_PAGE = 10
BIDS_PER_PAGE = 10


def mod11check(value):
    try:
        mod11codes.check(value)
    except (mod11codes.CheckDigitError, ValueError):
        raise ValidationError("Not a valid code")


class BidderAddForm(forms.Form):

    bidderid = forms.CharField(max_length=8, validators=[mod11check])
    name = forms.CharField(max_length=100)
    regid = forms.CharField(max_length=10)


BidderAddFormSet = formset_factory(BidderAddForm, extra=BIDDERS_PER_PAGE)


@permission_required('artshow.add_bidder')
def bulk_add(request):
    if request.method == "POST":
        formset = BidderAddFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                bidderid = form.cleaned_data.get('bidderid')
                if not bidderid:
                    continue
                name = form.cleaned_data['name']
                regid = form.cleaned_data['regid']
                person = Person(name=name, reg_id=regid)
                person.save()
                bidder = Bidder(person=person)
                bidder.save()
                bidderid = BidderId(id=bidderid, bidder=bidder)
                bidderid.save()
            return redirect('.')

    else:
        formset = BidderAddFormSet()
    return render(request, 'artshow/bidderbulkadd.html', dict(formset=formset))


class BidAddForm (forms.Form):

    piece = forms.CharField(max_length=8)
    bidder = forms.CharField(max_length=8, required=False, validators=[mod11check])
    TYPE_CHOICES = (
        ('nobids', 'No Bids'),
        ('normal', 'Normal Bid'),
        ('buynow', 'Buy Now'),
        ('auction', 'Auction'),
        ('nfs', 'Not For Sale'),
        ('', "Clear"),
    )
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.RadioSelect)
    amount = forms.IntegerField(required=False)

    piece_code_1 = re.compile(r"\s*(?P<artist_id>\d+)-(?P<piece_id>\d+)\s*$")
    piece_code_2 = re.compile(r"\s*[Aa](?P<artist_id>\d+)[Pp](?P<piece_id>\d+)\s*$")

    def clean_piece(self):
        piece_code = self.cleaned_data['piece']
        mo = self.piece_code_1.match(piece_code)
        if not mo:
            mo = self.piece_code_2.match(piece_code)
        if not mo:
            raise forms.ValidationError("Not in known format")
        artist_id = mo.group('artist_id')
        piece_id = mo.group('piece_id')
        try:
            piece = Piece.objects.get(artist__artistid=artist_id, pieceid=piece_id)
        except Piece.DoesNotExist:
            raise forms.ValidationError("Piece does not exist")
        return piece

    def clean_bidder(self):
        bidder_code = self.cleaned_data['bidder']
        try:
            bidder = Bidder.objects.get(bidderid__id=bidder_code)
        except Bidder.DoesNotExist:
            raise forms.ValidationError("Bidder does not exist")
        return bidder

    def clean(self):
        if self._errors:
            return self.cleaned_data

        cleaned_data = super(BidAddForm, self).clean()
        bidder = cleaned_data['bidder']
        type = cleaned_data['type']
        choices = dict(self.TYPE_CHOICES)
        type_text = choices[type]
        amount = cleaned_data['amount']

        if type in ('nobids', 'nfs'):
            if bidder:
                self._errors['bidder'] = self.error_class(["Bidder not permitted for type \"%s\"" % type_text])
                del cleaned_data['bidder']
            if amount:
                self._errors['amount'] = self.error_class(["Amount not permitted for type \"%s\"" % type_text])
                del cleaned_data['amount']
        else:
            if not bidder:
                self._errors['bidder'] = self.error_class(["Bidder required for type \"%s\"" % type_text])
                del cleaned_data['type']
            if not amount:
                self._errors['amount'] = self.error_class(["Amount required for type \"%s\"" % type_text])
                del cleaned_data['amount']

        return cleaned_data

BidAddFormSet = formset_factory(BidAddForm, extra=BIDS_PER_PAGE)


class BidAddOptionsForm (forms.Form):

    STAGE_CHOICES = (
        ('mid', "Before close. Bids not counted as final."),
        ('close', "After close, before Voice Auction. Non-Voice Auction bids counted as final."),
        ('final', "After close and Voice Auction. All bids counted as final."),
    )

    stage = forms.ChoiceField(choices=STAGE_CHOICES, widget=forms.RadioSelect)


@permission_required('artshow.add_bid')
def bid_bulk_add(request):
    if request.method == "POST":
        formset = BidAddFormSet(request.POST, prefix="bids")
        optionsform = BidAddOptionsForm(request.POST, prefix="options")
        if optionsform.is_valid() and formset.is_valid():
            stage = optionsform.cleaned_data['stage']
            for form in formset:
                ## xTODO something
                pass
            return redirect('.')
    else:
        formset = BidAddFormSet(prefix="bids")
        optionsform = BidAddOptionsForm(prefix="options")
    return render(request, 'artshow/bidbulkadd.html', dict(formset=formset, optionsform=optionsform))

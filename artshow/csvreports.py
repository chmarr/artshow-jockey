# Artshow Jockey
# Copyright (C) 2009-2012 Chris Cogdon
# See file COPYING for licence details

from . import unicodewriter
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from .models import *


@permission_required('artshow.view_artist')
def artists(request):
    ## TODO - This depends on the Person structure, which we want to move out into the model itself.

    artists = Artist.objects.all().order_by('artistid')
    spaces = Space.objects.all()
    checkoffs = Checkoff.objects.all()

    field_names = ['artistid', 'name', 'address1', 'address2', 'city', 'state', 'postcode',
                   'country', 'phone', 'email', 'regid', 'artistname', 'website', 'mailin', 'agent', 'reservationdate',
                   'nameforcheque']

    for space in spaces:
        field_names += ['req-' + space.shortname, 'alloc-' + space.shortname]

    for checkoff in checkoffs:
        field_names += ['chk-' + checkoff.shortname]

    field_names_d = {}
    for n in field_names:
        field_names_d[n] = n

    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename=artists.csv"
    c = unicodewriter.UnicodeDictWriter(response, field_names)
    c.writerow(field_names_d)

    for a in artists:
        d = dict(artistid=a.artistid, name=a.person.name, address1=a.person.address1, address2=a.person.address2,
                 city=a.person.city, state=a.person.state,
                 postcode=a.person.postcode, country=a.person.country, phone=a.person.phone, email=a.person.email,
                 regid=a.person.reg_id, artistname=a.artistname(),
                 website=a.website, mailin=a.mailin and "Yes" or "No",
                 agent=", ".join([p.name for p in a.agents.all()]),
                 reservationdate=str(a.reservationdate))
        for alloc in a.allocation_set.all():
            d['req-' + alloc.space.shortname] = str(alloc.requested)
            d['alloc-' + alloc.space.shortname] = str(alloc.allocated)
        for checkoff in a.checkoffs.all():
            d['chk-' + checkoff.shortname] = checkoff.shortname
        c.writerow(d)

    return response


# noinspection PyUnusedLocal
@permission_required('artshow.view_piece')
def pieces(request):
    pieces = Piece.objects.all().order_by('artist__artistid', 'pieceid')

    field_names = ['artistid', 'pieceid', 'code', 'artistname', 'title', 'media', 'min_bid', 'buy_now', 'adult',
                   'not_for_sale', 'status', 'top_bid', 'bought_now', 'voice_auction', 'bidder_name', 'bidder_ids']

    field_names_d = {}
    for n in field_names:
        field_names_d[n] = n

    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename=pieces.csv"
    c = unicodewriter.UnicodeDictWriter(response, field_names)
    c.writerow(field_names_d)

    for p in pieces:
        try:
            top_bid = p.top_bid()
        except Bid.DoesNotExist:
            top_bid = None
        d = dict(artistid=p.artist.artistid, pieceid=p.pieceid, code=p.code, artistname=p.artist.artistname(),
                 title=p.name, media=p.media, min_bid=p.min_bid, buy_now=p.buy_now, adult=p.adult and "Yes" or "No",
                 not_for_sale=p.not_for_sale and "Yes" or "No",
                 status=p.get_status_display(), top_bid=top_bid and top_bid.amount or "",
                 bought_now=top_bid and (top_bid.buy_now_bid and "Yes" or "No") or "",
                 voice_auction=p.voice_auction and "Yes" or "No",
                 bidder_name=top_bid and top_bid.bidder.name or "",
                 bidder_ids=top_bid and (", ".join(top_bid.bidder.bidder_ids()) or ""),
                 )
        c.writerow(d)

    return response


# noinspection PyUnusedLocal
@permission_required('artshow.view_bidder')
def bidders(request):
    ## TODO - This depends on the Person structure, which we want to move out into the model itself.

    bidders = Bidder.objects.all()

    field_names = ['primary_bidder_id', 'bidder_ids', 'name', 'address1', 'address2', 'city', 'state', 'postcode',
                   'country', 'phone', 'email', 'regid']

    field_names_d = {}
    for n in field_names:
        field_names_d[n] = n

    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename=bidders.csv"
    c = unicodewriter.UnicodeDictWriter(response, field_names)
    c.writerow(field_names_d)

    for b in bidders:
        bidder_ids = b.bidder_ids()
        if bidder_ids:
            primary_bidder_id = bidder_ids[0]
        else:
            primary_bidder_id = ""
        d = dict(primary_bidder_id=primary_bidder_id,
                 bidder_ids=", ".join(bidder_ids),
                 name=b.person.name, address1=b.person.address1, address2=b.person.address2, city=b.person.city,
                 state=b.person.state,
                 postcode=b.person.postcode, country=b.person.country, phone=b.person.phone, email=b.person.email,
                 regid=b.person.reg_id)
        c.writerow(d)

    return response


# noinspection PyUnusedLocal
@permission_required('artshow.view_payment')
def payments(request):
    payments = Payment.objects.all().order_by('id')

    field_names = ['paymentid', 'artistid', 'name', 'artistname', 'date', 'type', 'description', 'amount']

    field_names_d = {}
    for n in field_names:
        field_names_d[n] = n

    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename=payments.csv"
    c = unicodewriter.UnicodeDictWriter(response, field_names)
    c.writerow(field_names_d)

    for p in payments:
        d = dict(
            paymentid=p.id, artistid=p.artist.artistid, name=p.artist.name(), artistname=p.artist.artistname(),
            date=p.date, type=p.payment_type.name, description=p.description, amount=p.amount)
        c.writerow(d)

    return response


# noinspection PyUnusedLocal
@permission_required('artshow.view_cheque')
def cheques(request):
    cheques = ChequePayment.objects.all().order_by('date', 'number', 'id')

    field_names = ['artistid', 'name', 'artistname', 'payee', 'date', 'number', 'amount']

    field_names_d = {}
    for n in field_names:
        field_names_d[n] = n

    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename=cheques.csv"
    c = unicodewriter.UnicodeDictWriter(response, field_names)
    c.writerow(field_names_d)

    for q in cheques:
        d = dict(
            artistid=q.artist.artistid, name=q.artist.name(), artistname=q.artist.artistname(),
            payee=q.payee, date=q.date, number=q.number, amount=-q.amount)
        c.writerow(d)

    return response

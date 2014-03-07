from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model
from ...conf import settings
from ...models import *


Person = get_model(*settings.ARTSHOW_PERSON_CLASS.split('.', 1))


class Command(BaseCommand):
    args = '<stage ...>'
    help = "Load up the artshow database with test data. Stages are start, bids, auctions"

    def handle(self, *args, **options):

        for stage in args:
            method = "stage_" + stage
            try:
                attr = getattr(self, method)
            except AttributeError:
                raise CommandError("unknown stage %s" % stage)
            attr()

    def stage_start(self):
        ps = Person(name="Bill Baggins")
        ps.save()
        a = Artist(artistid=1, person=ps)
        a.save()
        p = Piece(artist=a, pieceid=1, name="Bill's First Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()
        p = Piece(artist=a, pieceid=2, name="Bill's Second Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()
        p = Piece(artist=a, pieceid=3, name="Bill's Third Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()

        ps = Person(name="Freddy Frodo")
        ps.save()
        a = Artist(artistid=2, person=ps)
        a.save()
        p = Piece(artist=a, pieceid=1, name="Freddy's First Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()
        p = Piece(artist=a, pieceid=2, name="Freddy's Second Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()
        p = Piece(artist=a, pieceid=3, name="Freddy's Third Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()

        ps = Person(name="Jenny Johnson")
        ps.save()
        a = Artist(artistid=3, person=ps)
        a.save()
        p = Piece(artist=a, pieceid=2, name="Jenny's First Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()
        p = Piece(artist=a, pieceid=2, name="Jenny's Second Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()
        p = Piece(artist=a, pieceid=3, name="Jenny's Third Piece", not_for_sale=False, adult=False, min_bid=10,
                  buy_now=20, status=Piece.StatusInShow)
        p.clean()
        p.save()

        ps = Person(name="Chris Wilkie")
        ps.save()
        b = Bidder(person=ps)
        b.save()
        bi = BidderId("1001", bidder=b)
        bi.save()

        ps = Person(name="Eric Gordon")
        ps.save()
        b = Bidder(person=ps)
        b.save()
        bi = BidderId("1021", bidder=b)
        bi.save()

    def stage_bids(self):
        bidder = Bidder.objects.get(person__name="Chris Wilkie")
        b = Bid(bidder=bidder, amount=15, piece=Piece.objects.get(code="1-1"))
        b.save()
        b = Bid(bidder=bidder, amount=20, buy_now_bid=True, piece=Piece.objects.get(code="2-2"))
        b.save()

    def stage_auctions(self):
        pass

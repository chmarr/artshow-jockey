from django.core.management.base import BaseCommand, CommandError
from artshow.models import *

class Command ( BaseCommand ):

	args = '<stage ...>'
	help = "Load up the artshow database with test data. Stages are start, bids, auctions"
	
	def handle ( self, *args, **options ):
	
		for stage in args:
			method = "stage_"+stage
			try:
				attr = getattr ( self, method )
			except AttributeError:
				raise CommandError ( "unknown stage %s" % stage )
			attr ()
			
	def stage_start ( self ):
		a = Artist ( artistid=1, name="Bill Baggins" )
		a.save()
		p = Piece ( artist=a, pieceid=1, name="Bill's First Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()
		p = Piece ( artist=a, pieceid=2, name="Bill's Second Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()
		p = Piece ( artist=a, pieceid=3, name="Bill's Third Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()

		a = Artist ( artistid=2, name="Freddy Frodo" )
		a.save()
		p = Piece ( artist=a, pieceid=1, name="Freddy's First Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()
		p = Piece ( artist=a, pieceid=2, name="Freddy's Second Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()
		p = Piece ( artist=a, pieceid=3, name="Freddy's Third Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()

		a = Artist ( artistid=3, name="Jenny Johnson" )
		a.save()
		p = Piece ( artist=a, pieceid=2, name="Jenny's First Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()
		p = Piece ( artist=a, pieceid=2, name="Jenny's Second Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()
		p = Piece ( artist=a, pieceid=3, name="Jenny's Third Piece", not_for_sale=False, adult=False, min_bid=10, buy_now=20, status=Piece.StatusInShow )
		p.clean ()
		p.save ()
		
		b = Bidder ( name="Chris Wilkie" )
		b.save ()
		bi = BidderId ( "1001", bidder=b )
		bi.save ()
		
		b = Bidder ( name="Eric Gordon" )
		b.save ()
		bi = BidderId ( "1021", bidder=b )
		bi.save ()

		
	def stage_bids ( self ):
		bidder = Bidder.objects.get ( name="Chris Wilkie" )
		b = Bid ( bidder=bidder, amount=15, piece=Piece.objects.get(code="1-1") )
		b.save ()
		b = Bid ( bidder=bidder, amount=20, buy_now_bid=True, piece=Piece.objects.get(code="2-2") )
		b.save ()
		
	def stage_auctions ( self ):
		pass
			
		
			
		
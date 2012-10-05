# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
import mod11codes
from django.core import urlresolvers
from django.contrib.auth.models import User
from decimal import Decimal
from django.conf import settings
import artshow_settings

class Space ( models.Model ):
	name = models.CharField ( max_length = 20 )
	shortname = models.CharField ( max_length = 8 )
	available = models.DecimalField ( max_digits=4, decimal_places=1 )
	price = models.DecimalField ( max_digits=4, decimal_places=2 )
	def allocated ( self ):
		allocated = self.allocation_set.aggregate(sum=Sum('allocated'))['sum']
		if allocated == None:
			return 0
		else:
			return allocated
	def remaining ( self ):
		return self.available - self.allocated()
	def waiting ( self ):
		data = self.allocation_set.aggregate(allocated=Sum('allocated'),requested=Sum('requested'))
		if data['allocated'] == None or data['requested'] == None:
			return 0
		else:
			return data['requested'] - data['allocated']
		
	def __unicode__ ( self ):
		return self.name


class Checkoff ( models.Model ):
	name = models.CharField ( max_length = 100 )
	shortname = models.CharField ( max_length = 100 )
	def __unicode__ ( self ):
		return "%s (%s)" % ( self.name, self.shortname )

	
	
class ManageableArtistManager ( models.Manager ):
	def get_query_set ( self ):
		pass


class Artist ( models.Model ):
	artistid = models.IntegerField ( primary_key=True )
	person = models.ForeignKey ( settings.ARTSHOW_PERSON_CLASS )
	publicname = models.CharField ( max_length = 100, blank=True )
	website = models.CharField ( max_length = 200, blank=True )
	mailin = models.BooleanField ()
	agents = models.ManyToManyField ( settings.ARTSHOW_PERSON_CLASS, related_name="agent_for", blank=True )
	reservationdate = models.DateField ( blank=True, null=True )
	notes = models.TextField ( blank=True )
	spaces = models.ManyToManyField ( Space, through="Allocation" )
	checkoffs = models.ManyToManyField ( Checkoff, blank=True )
	payment_to = models.ForeignKey ( settings.ARTSHOW_PERSON_CLASS, null=True, blank=True, related_name="receiving_payment_for" )
	def artistname ( self ):
		return self.publicname or self.person.name
	def is_showing ( self ):
		return self.allocation_set.aggregate(alloc=Sum('allocated'))['alloc'] > 0
	def is_active ( self ):
		return self.allocation_set.aggregate(req=Sum('requested'))['req'] > 0
	def used_locations ( self ):
		return [x[0] for x in self.piece_set.exclude(status=Piece.StatusNotInShow).distinct().values_list("location")]
	def balance ( self ):
		return self.payment_set.aggregate ( balance=Sum ( 'amount' ))['balance']
	def __unicode__ ( self ):
		return "%s (%s)" % ( self.artistname(), self.artistid )


class Allocation ( models.Model ):
	artist = models.ForeignKey ( Artist )
	space = models.ForeignKey ( Space )
	requested = models.DecimalField ( max_digits=4, decimal_places=1 )
	allocated = models.DecimalField ( max_digits=4, decimal_places=1 )
	def allocated_charge ( self ):
		return self.allocated * 10
	def __unicode__ ( self ):
		return "%s (%s) - %s/%s %s" % ( self.artist.artistname(), self.artist.artistid, self.allocated, self.requested, self.space.name )


class Bidder ( models.Model ):
	person = models.OneToOneField ( settings.ARTSHOW_PERSON_CLASS )
	notes = models.TextField ( blank=True )
	def bidder_ids ( self ):
		return [ b_id.id for b_id in self.bidderid_set.all().order_by('id') ]
	def top_bids ( self, unsold_only=False ):
		results = []
		bids = self.bid_set.filter ( invalid=False )
		for b in bids:
			if b.is_top_bid and ( not unsold_only or b.piece.status != Piece.StatusSold ):
				results.append ( b )
		return results
	def __unicode__ ( self ):
		ids = [ bidderid.id for bidderid in self.bidderid_set.all() ]
		return "%s (%s)" % ( self.person.name, ",".join(ids) )


class BidderId ( models.Model ):
	id = models.CharField ( max_length=8, primary_key=True )
	bidder = models.ForeignKey ( Bidder )
	def validate ( self ):
		try:
			mod11codes.check ( str(self.id) )
		except mod11codes.CheckDigitError:
			raise ValidationError ( "Bidder ID is not valid" )
		
	def __unicode__ ( self ):
		return "BidderId %s (%s)" % ( self.id, self.bidder.name )


class Piece ( models.Model ):
	artist = models.ForeignKey ( Artist )
	pieceid = models.IntegerField ()
	code = models.CharField ( max_length=10, editable=False )
	name = models.CharField ( max_length = 100 )
	media = models.CharField ( max_length = 100, blank=True )
	location = models.CharField ( max_length = 8, blank=True )
	not_for_sale = models.BooleanField ()
	adult = models.BooleanField ()
	min_bid = models.DecimalField ( max_digits=5, decimal_places=0, blank=True, null=True )
	buy_now = models.DecimalField ( max_digits=5, decimal_places=0, blank=True, null=True )
	voice_auction = models.BooleanField ( default=False )
	bidsheet_scanned = models.BooleanField ( default=False )
	
	StatusNotInShow = 0
	StatusInShow = 1
	StatusWon = 2
	StatusSold = 3
	StatusReturned = 4
	
	STATUS_CHOICES = [
		( StatusNotInShow, u'Not In Show' ),
		( StatusInShow, u'In Show' ),
		( StatusWon, u'Won' ),
		( StatusSold, u'Sold' ),
		( StatusReturned, u'Returned' ),
		]
	status = models.IntegerField ( choices=STATUS_CHOICES, default=StatusNotInShow )
	def artistname ( self ):
		return self.artist.publicname or self.artist.name
	def top_bid ( self ):
		return self.bid_set.exclude ( invalid=True ).order_by ( '-amount' )[0:1].get()
	def clean ( self ):
		self.code = "%s-%s" % ( self.artist.artistid, self.pieceid )
	def __unicode__ ( self ):
		return "%s - \"%s\" by %s" % ( self.code, self.name, self.artistname() )
		
class Product ( models.Model ):
	artist = models.ForeignKey ( Artist )
	productid = models.IntegerField ()
	name = models.CharField ( max_length = 100 )
	location = models.CharField ( max_length = 8, blank=True )
	adult = models.BooleanField ()
	price = models.DecimalField ( max_digits=5, decimal_places=2, blank=True, null=True )
	def artistname ( self ):
		return self.artist.publicname or self.artist.name
	def __unicode__ ( self ):
		return "A%sR%s - %s by %s (%s)" % ( self.artist.artistid, self.productid, self.name, self.artistname(), self.artist.artistid )

class Bid ( models.Model ):
	bidder = models.ForeignKey ( Bidder )
	amount = models.DecimalField ( max_digits=5, decimal_places=0 )
	piece = models.ForeignKey ( Piece )
	buy_now_bid = models.BooleanField ( default=False )
	invalid = models.BooleanField ( default=False )
	def _is_top_bid ( self ):
		return self.piece.top_bid() == self
	is_top_bid = property(_is_top_bid)
	def __unicode__ ( self ):
		bidderids = [ bidderid.id for bidderid in self.bidder.bidderid_set.all() ]
		return "%s (%s) %s $%s on %s" % ( self.bidder.name, ",".join(bidderids), "INVALID BID" if self.invalid else "bid", self.amount, self.piece )
	class Meta:
		unique_together = ( ('piece','amount','invalid'), )
	def validate ( self ):
		# super(Bid,self).validate()
		if self.piece.not_for_sale: raise ValidationError ( "Not For Sale piece cannot have bids placed on it" )
		if self.id == None:
			if self.piece.status != Piece.StatusInShow:
				raise ValidationError ( "New bids cannot be placed on pieces that are not In Show" )
			try:
				top_bid = self.piece.top_bid ()
				if self.amount <= top_bid.amount: 
					raise ValidationError ( "New bid must be higher than existing bids" )
				if self.piece.buy_now and top_bid.buy_now_bid:
					raise ValidationError ( "Cannot bid on piece that has had Buy Now option invoked" )
				if self.buy_now_bid:
					raise ValidationError ( "Buy Now option not available on piece with bids" )
			except Bid.DoesNotExist:
				pass
		if self.buy_now_bid:
			if not self.piece.buy_now:
				raise ValidationError ( "Buy Now option not available on this piece" )
			if self.amount < self.piece.buy_now:
				raise ValidationError ( "Buy Now bid cannot be less than Buy Now price" )
		if self.amount < self.piece.min_bid:
			raise ValidationError ( "Bid cannot be less than Min Bid" )
#	def save ( self ):
#		self.validate()
#		super(Bid,self).save()
		

class EmailTemplate ( models.Model ):
	name = models.CharField ( max_length = 100 )
	subject = models.CharField ( max_length = 100 )
	template = models.TextField ()
	template.help_text = "Begin a line with \".\" to enable word-wrap. Use Django template language. Variables \"artist\", \"pieces_in_show\", \"payments\" and \"artshow_settings\" are available."
	def __unicode__ ( self ):
		return self.name

class PaymentType ( models.Model ):
	name = models.CharField ( max_length=40 )
	def __unicode__ ( self ):
		return self.name

class Payment ( models.Model ):
	artist = models.ForeignKey ( Artist )
	amount = models.DecimalField ( max_digits=7, decimal_places=2 )
	payment_type = models.ForeignKey ( PaymentType )
	description = models.CharField ( max_length=100 )
	date = models.DateField ()
	def __unicode__ ( self ):
		return "%s (%s) %s %s" % ( self.artist.artistname(), self.artist.artistid, self.amount, self.date )
		
class ChequePayment ( Payment ):
	number = models.CharField ( max_length=10, blank=True )
	payee = models.CharField ( max_length=100, blank=True )
	def clean ( self ):
		if not self.payee:
			self.payee = self.artist.chequename ()
		if self.amount >= 0:
			raise ValidationError ( "Cheque amounts are a payment outbound and must be negative" )
		self.payment_type = PaymentType.objects.get(pk=artshow_settings.PAYMENT_SENT_PK)
		self.description = "Cheque %s Payee %s" % ( self.number and "#"+self.number or "pending number", self.payee )
		
class Invoice ( models.Model ):
	payer = models.ForeignKey ( Bidder )
	tax_paid = models.DecimalField ( max_digits=7, decimal_places=2, blank=True, null=True )
	def total_paid ( self ):
		return self.invoicepayment_set.aggregate ( sum=Sum('amount') )['sum'] or Decimal('0.0')
	paid_date = models.DateField ( blank=True, null=True )
	notes = models.TextField ( blank=True )
	def __unicode__ ( self ):
		return u"Invoice %d for %s" % ( self.id, self.payer )

class InvoicePayment ( models.Model ):
	amount = models.DecimalField ( max_digits=7, decimal_places=2 )
	PAYMENT_METHOD_CHOICES = [
		( 0, u"Not Paid" ),
		( 1, u"Cash" ),
		( 2, u"Check" ),
		( 3, u"Card" ),
		( 4, u"Other" ),
		]
	payment_method = models.IntegerField ( choices=PAYMENT_METHOD_CHOICES, default=0 )
	invoice = models.ForeignKey ( Invoice )

class InvoiceItem ( models.Model ):
	piece = models.OneToOneField ( Piece )
	invoice = models.ForeignKey ( Invoice )
	price = models.DecimalField ( max_digits=7, decimal_places=2 )
	def __unicode__ ( self ):
		return "%s for $%s" % ( self.invoice, self.price )


class BatchScan ( models.Model ):
	BATCHTYPES = [
		( 0, u"Unknown" ),
		( 1, u"Locations" ),
		( 2, u"Intermediate Bids" ),
		( 3, u"Final Bids" ),
		]
	batchtype = models.IntegerField ( choices=BATCHTYPES, default=0 )
	data = models.TextField ()
	date_scanned = models.DateTimeField ()
	processed = models.BooleanField ()
	processing_log = models.TextField ( blank=True )
	def __unicode__ ( self ):
		return u"BatchScan %s" % self.id

class Event ( models.Model ):
	name = models.CharField ( max_length=100 )
	occurred = models.BooleanField ( default=False )
	auto_occur = models.DateTimeField ( blank=True, null=True )
	def __unicode__ ( self ):
		return self.name
	

class Task ( models.Model ):
	summary = models.CharField ( max_length=100 )
	detail = models.TextField ( blank=True )
	time_entered = models.DateTimeField ()
	due_at = models.ForeignKey ( Event )
	actor = models.ForeignKey ( 'auth.User' )
	done = models.BooleanField ( default=False )
	def __unicode__ ( self ):
		return self.summary

class ArtistAccess ( models.Model ):
	user = models.ForeignKey ( User )
	artist = models.ForeignKey ( Artist )
	can_edit = models.BooleanField ( default=False )

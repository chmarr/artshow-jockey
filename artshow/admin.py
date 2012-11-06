# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from models import *
from django.contrib import admin, messages
from django.core import urlresolvers
from django.contrib.admin import helpers
from django import template
from django.shortcuts import render_to_response
from django.utils.html import escape
from django import forms
from django.db import models
import email1, processbatchscan
from django.core.mail import send_mail
import artshow_settings
import smtplib, datetime, decimal
from django.http import HttpResponse
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

class FormfieldOverrider ( object ):
	def formfield_for_dbfield ( self, db_field, **kwargs ):
		try:
			override = self.formfield_overrides2[db_field.name]
		except KeyError:
			pass
		else:
			kwargs['widget'] = override
		return super(FormfieldOverrider,self).formfield_for_dbfield ( db_field, **kwargs )

class TestWidget ( forms.TextInput ):
	def __init__ ( self ):
		super(TestWidget,self).__init__ ( attrs={'size':30} )

class PanelCountWidget ( forms.TextInput ):
	def __init__ ( self ):
		super(PanelCountWidget,self).__init__ ( attrs={'size':6} )

class PieceIdWidget ( forms.TextInput ):
	def __init__ ( self ):
		super(PieceIdWidget,self).__init__ ( attrs={'size':3} )

class BidTextWidget ( forms.TextInput ):
	def __init__ ( self ):
		super(BidTextWidget,self).__init__ ( attrs={'size':6} )

class MediaTextWidget ( forms.TextInput ):
	def __init__ ( self ):
		super(MediaTextWidget,self).__init__ ( attrs={'size':8} )
		
class LocationTextWidget ( forms.TextInput ):
	def __init__ ( self ):
		super(LocationTextWidget,self).__init__ ( attrs={'size':4} )	

class ArtistAccessInline ( admin.TabularInline ):
	model = ArtistAccess
	extra = 0

class AllocationInline ( FormfieldOverrider, admin.TabularInline ):
	model = Allocation
	extra = 1
	formfield_overrides2 = {
		'requested': PanelCountWidget,
		'allocated': PanelCountWidget,
		}

class PieceInline ( FormfieldOverrider, admin.TabularInline ):
	fields = ( "pieceid", "name", "media", "adult", "not_for_sale", "min_bid", "buy_now", "location", "voice_auction", "status" )
#	formfield_overrides = {
# 		'location': { 'widget': LocationTextWidget },
# 		}
	model = Piece
	extra = 5
	formfield_overrides2 = {
		'pieceid': PieceIdWidget,
		'media':   MediaTextWidget,
		'location': LocationTextWidget,
		'min_bid': BidTextWidget,
		'buy_now': BidTextWidget,
		'invoice_price': BidTextWidget,
		}
	ordering = ( 'pieceid', )
	
#class ProductInline ( admin.TabularInline ):
#	fields = ( "productid", "name", "adult", "price", "location" )
#	model = Product
#	extra = 1
#	ordering = ( 'productid', )

class PaymentInline ( admin.TabularInline ):
	model = Payment
	extra = 1

class ArtistAdmin ( AjaxSelectAdmin ):
	form = make_ajax_form(Artist,{'person':'person','agents':'person','payment_to':'person'})
	list_display = ( 'person_name', 'publicname', 'artistid', 'person_clickable_email', 'requested_spaces', 'allocated_spaces', 'person_mailing_label' )
	list_filter = ( 'mailin', 'person__country', 'checkoffs' )
	search_fields = ( 'person__name', 'publicname', 'person__email', 'notes', 'artistid' )
	fields = [ 'artistid', 'person', 'publicname', ( 'reservationdate', 'mailin' ), 'agents', 'notes', 'checkoffs', 'payment_to' ]
	inlines = [ArtistAccessInline,AllocationInline,PieceInline,PaymentInline]
	def requested_spaces ( self, artist ):
		return ", ".join ( "%s:%s" % (al.space.shortname,al.requested) for al in artist.allocation_set.all() )
	def allocated_spaces ( self, artist ):
		return ", ".join ( "%s:%s" % (al.space.shortname,al.allocated) for al in artist.allocation_set.all() )
	def person_name ( self, artist ):
		return artist.person.name
	def person_clickable_email ( self, artist ):
		return artist.person.clickable_email()
	person_clickable_email.allow_tags = True
	def person_mailing_label ( self, artist ):
		return artist.person.mailing_label()
	person_mailing_label.allow_tags = True	
		
	def send_email ( self, request, queryset ):
		opts = self.model._meta
		app_label = opts.app_label
		emails = []
		template_id = None
		if request.POST.get('post'):
			template_id = request.POST.get('template')
			if not template_id:
				messages.error ( request, "Please select a template" )
			else:
				template_id = int(template_id)
				selected_template = EmailTemplate.objects.get(pk=template_id)
				if request.POST.get('send_email'):
					for a in queryset:
						body = email1.make_email ( a, selected_template.template )
						try:
							send_mail ( selected_template.subject, body, artshow_settings.ARTSHOW_EMAIL_SENDER, [ a.email ], fail_silently=False )
							self.message_user ( request, "Mail to %s succeeded" % a.email )
						except smtplib.SMTPException, x:
							# TODO - use a error indicator
							self.message_user ( request, "Mail to %s failed: %s" % ( a.email, x ) )
					return None
				else:
					for a in queryset:
						emails.append ( { 'to': a.email, 'body':email1.make_email ( a, selected_template.template ) } )
		templates = EmailTemplate.objects.all()
		context = {
			"title": "Send E-mail to Artists",
			"queryset": queryset,
			"opts": opts,
			"root_path": self.admin_site.root_path,
			"app_label": app_label,
			"action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
			"templates": templates,
			"emails": emails,
			"template_id": template_id,
			}
		return render_to_response ( "admin/email_selected_confirmation.html", context, context_instance=template.RequestContext(request))
	send_email.short_description = "Send E-mail"
		
	def print_bidsheets ( self, request, queryset ):
		import bidsheets
		response = HttpResponse ( mimetype="application/pdf" )
		bidsheets.generate_bidsheets_from_queryset ( template_pdf=artshow_settings.ARTSHOW_BLANK_BID_SHEET, output=response, artists=queryset )
		self.message_user ( request, "Bid sheets printed." )
		return response
	print_bidsheets.short_description = "Print Bid Sheets"
	
	def apply_space_fees ( self, request, artists ):
		payment_type = PaymentType.objects.get(pk=artshow_settings.SPACE_FEE_PK)
		for a in artists:
			total = 0
			for alloc in a.allocation_set.all():
				total += alloc.space.price * alloc.allocated
			if total > 0:
				allocated_spaces_str = ", ".join ( "%s:%s" % (al.space.shortname,al.allocated) for al in a.allocation_set.all() )
				payment = Payment ( artist=a, amount=-total, payment_type=payment_type, description=allocated_spaces_str, date=datetime.datetime.now() )
				payment.save ()
	
	def apply_winnings_and_commission ( self, request, artists ):
		pt_winning = PaymentType.objects.get(pk=artshow_settings.SALES_PK)
		pt_commission = PaymentType.objects.get(pk=artshow_settings.COMMISSION_PK)
		for a in artists:
			total_winnings = 0
			total_pieces = 0
			pieces_with_bids = 0
			for piece in a.piece_set.all():
				if piece.status != Piece.StatusNotInShow:
					total_pieces += 1
				try:
					top_bid = piece.top_bid()
					total_winnings += top_bid.amount
					pieces_with_bids += 1
				except Bid.DoesNotExist:
					pass
			commission = total_winnings * decimal.Decimal(artshow_settings.ARTSHOW_COMMISSION)
			if total_pieces > 0:
				payment = Payment ( artist=a, amount=total_winnings, payment_type=pt_winning, description="%d piece%s, %d with bid%s" % ( total_pieces, total_pieces!=1 and "s" or "", pieces_with_bids, pieces_with_bids != 1 and "s" or ""), date=datetime.datetime.now() )
				payment.save ()
			if commission > 0:
				payment = Payment ( artist=a, amount=-commission, payment_type=pt_commission, 
						description="%s%% of sales" % (decimal.Decimal(artshow_settings.ARTSHOW_COMMISSION) * 100),
						date=datetime.datetime.now() )
				payment.save ()
	
	def create_cheques ( self, request, artists ):
		pt_paymentsent = PaymentType.objects.get ( pk=artshow_settings.PAYMENT_SENT_PK )
		for a in artists:
			balance = a.payment_set.aggregate ( balance=Sum ( 'amount' ) )['balance']
			if balance > 0:
				chq = ChequePayment ( artist=a, payment_type=pt_paymentsent, amount=-balance, date=datetime.datetime.now() )
				chq.clean ()
				chq.save ()
				
	def allocate_spaces ( self, request, artists ):
		artists = artists.order_by ( 'reservationdate', 'artistid' )
		spaces_remaining = {}
		for space in Space.objects.all ():
			spaces_remaining[space.id] = space.remaining ()
		for artist in artists:
			for alloc in artist.allocation_set.all ():
				needed = alloc.requested - alloc.allocated
				to_allocate = min ( needed, spaces_remaining[alloc.space.id] )
				if to_allocate > 0:
					alloc.allocated += to_allocate
					spaces_remaining[alloc.space.id] -= to_allocate
					alloc.save ()
	
	actions = ('send_email','print_bidsheets','apply_space_fees','apply_winnings_and_commission','create_cheques','allocate_spaces')
	filter_horizontal = ('checkoffs',)
		
admin.site.register(Artist,ArtistAdmin)

class SpaceAdmin ( admin.ModelAdmin ):
	list_display = ( 'name', 'shortname', 'price', 'available', 'allocated', 'remaining', 'waiting' )

admin.site.register(Space,SpaceAdmin)

class BidInline ( admin.TabularInline ):
	model = Bid
	raw_id_fields = ( 'bidder', )
	extra = 1

class PieceAdmin ( admin.ModelAdmin ):
	def clear_scanned_flag ( self, request, pieces ):
		pieces.update ( bidsheet_scanned=False )
		self.message_user ( request, "Bidsheet_scanned flags have been cleared." )
	
	def set_scanned_flag ( self, request, pieces ):
		pieces.exclude(status=Piece.StatusNotInShow).update ( bidsheet_scanned=True )
		self.message_user ( request, "Bidsheet_scanned flags have been set if the piece is or was in show." )
	
	def clear_won_status ( self, request, pieces ):
		pieces.filter(status=Piece.StatusWon).update ( status=Piece.StatusInShow )
		self.message_user ( request, "Pieces marked as 'Won' have been returned to 'In Show'." )
	
	def apply_won_status ( self, request, pieces ):
		for p in pieces.filter(status=Piece.StatusInShow,voice_auction=False):
			try:
				top_bid = p.top_bid()
			except ObjectDoesNotExist:
				pass
			else:
				p.status = Piece.StatusWon
				p.save ()
		self.message_user ( request, "Pieces marked as 'In Show', not in Voice Auction and has a bid have been marked as 'Won'." )
	
	def apply_won_status_incl_voice_auction ( self, request, pieces ):
		for p in pieces.filter(status=Piece.StatusInShow):
			try:
				top_bid = p.top_bid()
			except ObjectDoesNotExist:
				pass
			else:
				p.status = Piece.StatusWon
				p.save ()
		self.message_user ( request, "Pieces marked as 'In Show' and has a bid have been marked as 'Won'." )
	
	def apply_returned_status ( self, request, pieces ):
		pieces.filter (status=Piece.StatusInShow).update ( status=Piece.StatusReturned )
		self.message_user ( request, "Pieces marked as 'In Show' have been marked 'Returned'." )

	def clickable_artist ( self, obj ):
		return u'<a href="%s">%s</a>' % ( urlresolvers.reverse('admin:artshow_artist_change',args=(obj.artist.pk,)), escape(obj.artist.artistname()) )
	clickable_artist.allow_tags = True
	clickable_artist.short_description = "Artist"
	def clickable_invoice ( self, obj ):
		return u'<a href="%s">%s</a>' % ( urlresolvers.reverse('admin:artshow_invoice_change',args=(obj.invoice.id,)), obj.invoice )
	clickable_invoice.allow_tags = True
	clickable_invoice.short_description = "Invoice"
	def top_bid ( self, obj ):
		return obj.bid_set.exclude ( invalid=True ).order_by ( '-amount' )[0:1].get().amount
	def min_bid_x ( self, obj ):
		if obj.not_for_sale or obj.min_bid == None:
			return "NFS"
		else:
			return obj.min_bid
	min_bid_x.short_description = "Min Bid"
	def buy_now_x ( self, obj ):
		if obj.buy_now == None:
			return "N/A"
		else:
			return obj.buy_now
	buy_now_x.short_description = "Buy Now"
	list_filter = ( 'adult', 'not_for_sale', 'voice_auction', 'status', 'bidsheet_scanned' )
	search_fields = ( '=code', '=artist__artistid', 'name', '=location', 'artist__name', 'artist__publicname' )
	list_display = ( 'code', 'clickable_artist', 'name', 'adult', 'min_bid_x', 'buy_now_x', 'location', 'voice_auction', 'status', 'top_bid' )
	inlines = [BidInline]
	# raw_id_fields = ( 'invoice', )
	# TODO put 'invoiceitem' back into the list. Waiting on bug #16433
	fields = ( 'artist', 'pieceid', 'name', 'media', 'location', 'not_for_sale', 'adult', 'min_bid', 'buy_now', 'voice_auction', 'bidsheet_scanned', 'status', 'top_bid' )
	raw_id_fields = ( 'artist', )
	readonly_fields = ( 'top_bid', 'invoiceitem', )
	actions = ( 'clear_scanned_flag', 'set_scanned_flag', 'clear_won_status', 'apply_won_status', 'apply_won_status_to_voice_auction', 'apply_returned_status' )

admin.site.register(Piece,PieceAdmin)

#admin.site.register(Product)

class BidderIdInline ( admin.TabularInline ):
	model = BidderId
	
class BidInline ( admin.TabularInline ):
	model = Bid
	fields = ( 'piece', 'amount', 'buy_now_bid', 'invalid' )
	raw_id_fields = ( 'piece', )
	
class BidderAdmin ( AjaxSelectAdmin ):
	form = make_ajax_form(Bidder,{'person':'person'})
	def bidder_ids ( self, obj ):
		return u", ".join ( [ bidderid.id for bidderid in obj.bidderid_set.all() ] )
	def person_name ( self, bidder ):
		return bidder.person.name
	def person_clickable_email ( self, bidder ):
		return bidder.person.clickable_email ()
	person_clickable_email.allow_tags = True
	
	# TODO, add mailing_label back in once we figure out how to do it for bidders and artists uniformly
	list_display = ( 'person_name', 'bidder_ids', 'person_clickable_email' )
	search_fields = ( 'person__name', 'bidderid__id' )
	fields = [ "person", "notes" ]
	inlines = [BidderIdInline,BidInline]

admin.site.register(Bidder,BidderAdmin)

class EmailTemplateAdmin ( admin.ModelAdmin ):
	save_as = True

admin.site.register(EmailTemplate,EmailTemplateAdmin)

class PaymentAdmin ( admin.ModelAdmin ):
	list_display = ( 'artist', 'amount', 'payment_type', 'description', 'date' )
	list_filter = ( 'payment_type', )
	date_hierarchy = 'date'
	raw_id_fields = ( 'artist', )

admin.site.register(Payment,PaymentAdmin)

admin.site.register(PaymentType)

class InvoiceItemInline ( admin.TabularInline ):
	model = InvoiceItem
	# fields = ( 'piece', 'top_bid', 'price', )
	fields = ( 'piece', 'price', )
	raw_id_fields = ( 'piece', )
	# read_only_fields = ( 'top_bid', )
	# formfield_overrides2 = {
		# 'top_bid': TestWidget,
	# }
	
class InvoicePaymentInline ( admin.TabularInline ):
	model = InvoicePayment

class InvoiceAdmin ( admin.ModelAdmin ):
	def bidder_name ( self, obj ):
		return obj.payer.name
	def num_pieces ( self, obj ):
		return obj.invoiceitem_set.count()
	raw_id_fields = ( 'payer', )
	list_display = ( 'id', 'bidder_name', 'num_pieces', 'total_paid' )
	search_fields = ( 'id', 'payer__name' )
	inlines = [InvoiceItemInline,InvoicePaymentInline]
	

admin.site.register(Invoice,InvoiceAdmin)

class BidAdmin ( admin.ModelAdmin ):
	raw_id_fields = ( "bidder", "piece" )

admin.site.register(Bid,BidAdmin)

class CheckoffAdmin ( admin.ModelAdmin ):
	list_display = ( 'name', 'shortname' )

admin.site.register(Checkoff,CheckoffAdmin)

class BatchScanAdmin ( admin.ModelAdmin ):
	list_display = ( 'id', 'batchtype', 'date_scanned', 'processed' )
	list_filter = ( 'batchtype', 'processed', )
	fields = ( 'id', 'batchtype', 'data', 'date_scanned', 'processed', 'processing_log' )
	readonly_fields = ( 'id', )
	actions = ('process_batch',)
	
	def process_batch ( self, request, queryset ):
		opts = self.model._meta
		for bs in queryset:
			processbatchscan.process_batchscan ( bs.id )
			self.message_user ( request, "Processed batch %d" % bs.id )
	process_batch.short_description = "Process Batch"
	

admin.site.register(BatchScan,BatchScanAdmin)

# class BidderIdAdmin ( admin.ModelAdmin ):
#	list_display = ( 'id', 'bidder' )
#	search_fields = ( 'id', )
#	raw_id_fields = ( 'bidder', )

#admin.site.register(BidderId,BidderIdAdmin)

#admin.site.register(Event)

#class TaskAdmin ( admin.ModelAdmin ):
#	def due_at_date ( self, task ):
#		return task.due_at.auto_occur
#	def due_occurred ( self, task ):
#		return task.due_at.occurred
#	list_display = ( 'summary', 'due_at', 'due_at_date', 'due_occurred', 'done', 'actor' )
#	list_filter = ( 'done', 'actor' )

#admin.site.register(Task,TaskAdmin)

class ChequePaymentAdmin ( admin.ModelAdmin ):
	def cheque_amount ( self, obj ):
		return -obj.amount
	def print_cheques ( self, request, cheqs ):
		import cheques
		response = HttpResponse ( mimetype="text/plain" )
		for c in cheqs:
			cheques.cheque_to_text ( c, response )
		return response

	list_display = ( 'artist', 'date', 'payee', 'number', 'cheque_amount' )
	list_editable = ( 'number', )
	search_fields = ( 'artist__artistid', 'artist__name', 'payee', 'number' )
	fields = ( 'artist', 'date', 'payee', 'number', 'amount' )
	raw_id_fields = ( 'artist', )
	actions = ('print_cheques',)

admin.site.register ( ChequePayment, ChequePaymentAdmin )

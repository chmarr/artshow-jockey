#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from models import BatchScan, Piece, Bidder, Bid, BidderId
import datetime, re
from django.db.models.query import transaction
from django.core.exceptions import ValidationError

class BatchProcessingError ( Exception ):
	def __init__ ( self, detail, errorlist ):
		self.detail = detail
		self.errorlist = errorlist
	def __str__ ( self ):
		return "%s: %d errors listed" % ( self.detail, len(self.errorlist) )


location_scan_re = re.compile ( r'[PL](\w\d+)$' )
piece_scan_re = re.compile ( r'A(\d+)P(\d+)$' )
end_location_scan_re = re.compile ( r'[PL]END$' )

bidder_scan_re = re.compile ( r'B(\d+)$' )
price_scan_re = re.compile ( r'(\d+)$' )
normal_sale_scan_re = re.compile ( r'NS$' )
buy_now_scan_re = re.compile ( r'NBN$' )
no_bids_scan_re = re.compile ( r'NB$' )
auction_sale_scan_re = re.compile ( r'NAS$' )
auction_complete_scan_re = re.compile ( r'NAC$' )
not_for_sale_scan_re = re.compile ( r'NFS$' )

class StateL:
	start = 1
	read_location = 2
	error_skipping = 99

@transaction.commit_on_success
def process_locations ( data ):
	errors = []
	state = StateL.start
	lines = 0
	current_location = None
	for l in data.splitlines ():
		lines += 1
		l = l.strip()
		if l == "": continue
		mo = location_scan_re.match ( l )
		if mo:
			if state not in [ StateL.start, StateL.error_skipping ]:
				errors.append ( "line %d: previous block incomplete" % lines )
			current_location = mo.group(1)
			state = StateL.read_location
		if not mo:
			if state == StateL.error_skipping:
				continue
			mo = piece_scan_re.match ( l )
			if mo:
				if state == StateL.read_location:
					try:
						piece = Piece.objects.get ( artist=int(mo.group(1)), pieceid=int(mo.group(2)) )
					except Piece.DoesNotExist:
						errors.append ( "line %d: piece %s does not exist" % ( lines, l ) )
						state = State.error_skipping
						continue
					piece.location = current_location
					if piece.status == Piece.StatusNotInShow: piece.status = Piece.StatusInShow
					piece.save ()
				else:
					errors.append ( "line %d: piece %s not found immediately after location" % ( lines, l ) )
		if not mo:
			mo = end_location_scan_re.match ( l )
			if mo:
				if state == StateL.read_location:
					state = StateL.start
				else:
					errors.append ( "line %d: location block ended without being begun" % lines )
		if not mo:
			errors.append ( "line %d: unknown code %s"% ( lines, l ) )
			state = StateL.error_skipping
	if state != StateL.start:
		errors.append ( "END: block incomplete" )
						
	if errors:
		raise BatchProcessingError ( "found errors in processing", errors )
				
			

class State:
	start = 1
	read_piece = 2
	read_bidder = 3
	read_price = 4
	error_skipping = 99

@transaction.commit_on_success
def process_bids ( data, final_scan=False ):
	errors = []
	state = State.start
	lines = 0
	current_piece = None
	current_bidder = None
	current_price = None
	for l in data.splitlines ():
		lines += 1
		l = l.strip()
		if l == "":
			continue
		mo = piece_scan_re.match ( l )
		if mo:
			if state not in [ State.start, State.error_skipping ]:
				errors.append ( "line %d: previous block incomplete" % lines )
			try:
				current_piece = Piece.objects.get ( artist=int(mo.group(1)), pieceid=int(mo.group(2)) )
			except Piece.DoesNotExist:
				errors.append ( "line %d: piece %s does not exist" % ( lines, l ) )
				state = State.error_skipping
			else:
				state = State.read_piece
		if not mo:
			if state == State.error_skipping:
				continue
			mo = bidder_scan_re.match ( l )
			if mo:
				if state == State.read_piece:
					try:
						current_bidder = BidderId.objects.get ( id=mo.group(1) ).bidder
					except BidderId.DoesNotExist:
						errors.append ( "line %d: bidder %s does not exist" % ( lines, l ) )
						state = State.error_skipping
					else:
						state = State.read_bidder
				else:
					errors.append ( "line %d: found bidder scan not immediately after piece" % lines )
					state = State.error_skipping
		if not mo:
			mo = price_scan_re.match ( l )
			if mo:
				if state == State.read_bidder:
					current_price = int(mo.group(1))
					state = State.read_price
				else:
					errors.append ( "line %d: found price not immediately after bidder" % lines )
					state = State.error_skipping
		if not mo:
			mo = normal_sale_scan_re.match ( l )
			if mo:
				if state == State.start:
					# Skipping extraneous Normal Sale, a common scanning error
					pass
				elif state == State.read_price:
					bid = Bid ( bidder=current_bidder, amount=current_price, piece=current_piece )
					try:
						bid.validate ()
					except ValidationError, x:
						errors.append ( "line %d: invalid bid: %s" % ( lines, x ) )
						continue
					bid.save ()
					if final_scan:
						current_piece.bidsheet_scanned = True
						current_piece.status = Piece.StatusWon
					current_piece.save ()
					state = State.start
				else:
					errors.append ( "Line %d: normal sale scan found not immediately after price" % lines )
					state = State.error_skipping
		if not mo:
			mo = buy_now_scan_re.match ( l )
			if mo:
				if state == State.read_price:
					bid = Bid ( bidder=current_bidder, amount=current_price, piece=current_piece, buy_now_bid=True )
					try:
						bid.validate ()
					except ValidationError, x:
						errors.append ( "line %d: invalid bid: %s" % ( lines, x ) )
						state = State.error_skipping
						continue
					bid.save ()
					if final_scan:
						current_piece.bidsheet_scanned = True
						current_piece.status = Piece.StatusWon
					current_piece.save ()
					state = State.start
				else:
					errors.append ( "Line %d buy now scan found not immediately after price" % lines )
					state = State.error_skipping
		if not mo:
			mo = auction_sale_scan_re.match ( l )
			if mo:
				if state == State.read_price:
					bid = Bid ( bidder=current_bidder, amount=current_price, piece=current_piece )
					try:
						bid.validate ()
					except ValidationError, x:
						errors.append ( "line %d: invalid bid: %s" % ( lines, x ) )
						state = State.error_skipping
						continue
					bid.save ()
					if final_scan:
						current_piece.bidsheet_scanned = True
					current_piece.voice_auction = True
					current_piece.save ()
					state = State.start
					pass
				else:
					errors.append ( "Line %d auction sale scan found not immediately after price" % lines )
					state = State.error_skipping
		if not mo:
			mo = auction_complete_scan_re.match ( l )
			if mo:
				if state == State.read_price:
					bid = Bid ( bidder=current_bidder, amount=current_price, piece=current_piece )
					try:
						bid.validate ()
					except ValidationError, x:
						errors.append ( "line %d: invalid bid: %s" % ( lines, x ) )
						state = State.error_skipping
						continue
					bid.save ()
					if final_scan:
						current_piece.bidsheet_scanned = True
						current_piece.status = Piece.StatusWon
					current_piece.voice_auction = True
					current_piece.save ()
					state = State.start
					pass
				else:
					errors.append ( "Line %d auction sale scan found not immediately after price" % lines )
					state = State.error_skipping
		if not mo:
			mo = not_for_sale_scan_re.match ( l )
			if mo:
				if state == State.read_piece:
					if not current_piece.not_for_sale:
						errors.append ( "Line %d Not for sale found on non NFS piece" % lines )
						state = State.error_skipping
						continue
					if final_scan:
						current_piece.bidsheet_scanned = True
					current_piece.save()
					state = State.start
					pass
				else:
					errors.append ( "Line %d: not for sale scan found not immediately after piece" % lines )
					state = State.error_skipping
		if not mo:
			mo = no_bids_scan_re.match ( l )
			if mo:
				if state == State.read_piece:
					len = current_piece.bid_set.count()
					if len > 0:
						errors.append ( "Line %d: No Bid found for pieces with bids" % lines )
						state = State.error_skipping
						continue
					if final_scan:
						current_piece.bidsheet_scanned = True
					current_piece.save ()
					state = State.start
				else:
					errors.append ( "Line %d: no bids scan found not immediately after piece" % lines )
					state = State.error_skipping
				
		if not mo:
			errors.append ( "Line %d: found unknown line %s" % ( lines, l ) )
			state = State.error_skipping
	if state != StateL.start:
		errors.append ( "END: block incomplete" )

	if errors:
		raise BatchProcessingError ( "found errors in processing", errors )


		
def process_batchscan ( id ):
	batchscan = BatchScan.objects.get(id=id)
	now = datetime.datetime.now ()
	if batchscan.processed:
		log_str = "%s\nAlready Processed" % now
		batchscan.processing_log = log_str
		batchscan.save ()
	elif batchscan.batchtype not in [1,2]:
		log_str = "%s\nUnknown batchtype" % now
		batchscan.processing_log = log_str
		batchscan.save ()
	else:
		try:
			if batchscan.batchtype == 1:
				process_locations ( batchscan.data )
			elif batchscan.batchtype in [2,3]:
				process_bids ( batchscan.data, final_bids=batchscan.batchtype==3 )
		except BatchProcessingError, x:
			log_str = "\n".join ( [str(now),str(x)] + x.errorlist )
			batchscan.processing_log = log_str
			batchscan.save ()
		else:
			log_str = "%s\nProcessing Complete" % now
			batchscan.processing_log = log_str
			batchscan.processed = True
			batchscan.save ()

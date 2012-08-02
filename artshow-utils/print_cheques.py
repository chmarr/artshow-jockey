#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

import sys, os, re, num2word, time, optparse
from decimal import Decimal
from artshow.models import Artist


class DETAILS:
	artist_id = None
	name = None
	fan_name = None
	address1 = None
	address2 = None
	city = None
	state = None
	zip = None
	country = None
	check_name = None

	def __init__ ( self ):
		self.items = []

	def normalise ( self ):
		self.address2 = self.address2 or ""
		for attr in [ 'name','address1','address2','city','state','zip','country','check_name']:
			setattr ( self, attr, ( getattr ( self, attr ) or "").upper() )
		self.cheque_amount = reduce ( lambda x, y: x + y.amount, self.items, Decimal(0) )
		if not self.check_name:
			self.check_name = self.name


class ITEM:
	name = None
	amount = None

	def __init__ ( self, name=None, amount=None ):
		self.name=name
		self.amount=amount


class PRINT_GRID:
	x_size = 87
	y_size = 66
	def __init__ ( self ):
		self.data = [ " "*self.x_size for i in range(self.y_size) ]
	def print_at ( self, x, y, msg ):
		if x + len(msg) - 1 > self.x_size:
			raise Exception ( "line too long" )
		msg_len = len(msg)
		s = self.data[y-1]
		s = s[:x-1] + msg + s[x-1+msg_len:]
		self.data[y-1] = s
		self.last_line_printed = y
	def print_on_next_line ( self, msg ):
		self.print_at ( 1, self.last_line_printed+1, msg )
	def save ( self, filename ):
		f = open ( filename, "w" )
		for line in self.data:
			f.write ( line + "\n" )
		f.close ()


def dotpad ( s, max ):

	l = len(s)

	if l >= max:
		return s

	s += " " * (( max-l ) % 4)
	s += "  .." * ((max-l) / 4 )

	return s



def print_items ( details, grid, offset ):

	date_str = time.strftime ( "%d %b %Y", time.localtime(details.cheque_date) ).upper()

	s = "(%d) %s" % ( details.artist_id, details.name )
	if details.fan_name:
		s += " (%s)" % details.fan_name

	grid.print_at ( 1, offset, s )
	grid.print_at ( 77, offset, date_str )

	grid.last_line_printed = offset+1
	
	item_no = 0
	for item in details.items:
		item_no += 1
		name = dotpad ( item.name, 71 )
		grid.print_on_next_line ( " %2d. %-71s $%8.2f" % ( item_no, name, item.amount ) )

	grid.print_on_next_line ( "-"*87 )
	grid.print_on_next_line ( "     %-71s $%8.2f" % ( "Total, and cheque amount", details.cheque_amount ) )

	grid.print_on_next_line ( "" )
	grid.print_on_next_line ( "Thank you for exhibiting at FurCon 2012! Please direct any questions to" )
	grid.print_on_next_line ( "artshow@furtherconfusion.org, or by mail at the address above." )


def create_and_save_cheque ( details, filename ):

	details.normalise ()

	if details.cheque_amount <= 0:
		print >> sys.stderr, "Artist: %s (%d): Amount is %s: not generating" % ( details.fan_name, details.artist_id, details.cheque_amount )
		return

	if not details.address1:
		print >> sys.stderr, "Artist: %s (%d): Address1 is blank: generating anyway" % ( details.fan_name, details.artist_id )

	date_str = time.strftime ( "%d %b %Y", time.localtime(details.cheque_date) ).upper()

	cheque_dollars = int(details.cheque_amount)
	cheque_cents = int ((details.cheque_amount - cheque_dollars) * 100 + Decimal("0.5") )

	cheque_words = "** " + num2word.n2w.to_cardinal ( cheque_dollars ) + " dollars and %d cents" % cheque_cents + " **"
	cheque_words = cheque_words.upper ()

	grid = PRINT_GRID ()

	grid.print_at ( 77, 3, date_str )

	grid.print_at ( 8, 7, details.check_name )
	grid.print_at ( 77, 7, "$%-8.2f" % details.cheque_amount )

	grid.print_at ( 1, 9, cheque_words )

	grid.print_at ( 9, 14, details.name )
	grid.print_at ( 9, 15, details.address1 )

	if details.address2:
		grid.print_at ( 9, 16, details.address2 )
		one_if_no_address2 = 0
	else:
		one_if_no_address2 = 1
	
	grid.print_at ( 9, 17-one_if_no_address2, "%s %s  %s" % ( details.city, details.state, details.zip ) )

	if details.country and details.country != "USA":
		grid.print_at ( 9, 18-one_if_no_address2, details.country )

	print_items ( details, grid, 23 )
	print_items ( details, grid, 46 )

	grid.save ( filename )


def print_test_cheque ():

	d = DETAILS ()
	d.name = "Hello There"
	d.artist_id = 13
	d.fan_name = "Bottlebrush fox"
	d.address1 = "123 Main St."
	d.address2 = "Apt 123"
	d.city = "Brownsville"
	d.state = 'XY'
	d.zip = "12345-4432"
	d.country = "Australia"

	d.cheque_date = time.time()

	d.items.append ( ITEM ( "Payment received", 40 ) )
	d.items.append ( ITEM ( "Payment received", 12 ) )
	d.items.append ( ITEM ( "Panel Charge", -30 ) )
	d.items.append ( ITEM ( "Total of winning bids", Decimal("672.0") ) )
	d.items.append ( ITEM ( "10% Commission on winning bids", Decimal("-67.2") ) )
	d.items.append ( ITEM ( "Postage for returned artwork", Decimal("6.66") ) )

	create_and_save_cheque ( d, "testcheque" )


def print_cheques ( ids ):

	if ids:
		artists = Artist.objects.filter ( artistid__in=ids )
	else:
		artists = Artist.objects.all ()

	for a in artists:
		print_cheque ( a )


def print_cheque ( artist ):

	details = DETAILS ()
	details.artist_id = artist.artistid
	details.name = artist.name
	details.fan_name = artist.artistname()
	details.address1 = artist.address1
	details.address2 = artist.address2
	details.city = artist.city
	details.state = artist.state
	details.zip = artist.postcode
	details.country = artist.country
	details.check_name = artist.chequename()

	details.cheque_date = time.time()

	for p in artist.payment_set.all():
		details.items.append ( ITEM ( p.description, p.amount ) )
		
	create_and_save_cheque ( details, "cheque-%d" % artist.artistid )


def get_options ():
	parser = optparse.OptionParser ()
	parser.add_option ( "--ids", type="str", default=None )
	parser.add_option ( "--test", default=False, action="store_true" )
	opts, args = parser.parse_args ()
	if opts.ids:
		opts.ids = opts.ids.split(",")
		opts.ids = [int(x) for x in opts.ids]
	return opts


if __name__ == "__main__":
	opts = get_options ()
	if opts.test:
		print_test_cheque ()
	else:
		print_cheques ( opts.ids )

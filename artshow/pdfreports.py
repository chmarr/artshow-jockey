# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from django.db.models import Min
from artshow.models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch 
from reportlab.lib import colors

from cgi import escape

MAX_PIECES_PER_PAGE = 30

@permission_required ( 'artshow.is_artshow_staff' )
def winning_bidders ( request ):

	bidders = Bidder.objects.all().annotate(first_bidderid=Min('bidderid')).order_by('first_bidderid')
	response = HttpResponse ( mimetype="application/pdf" )
	
	styles = getSampleStyleSheet()	
	normal_style = styles["Normal"]
	heading_style = styles["Heading3"]
	heading_style_white = ParagraphStyle ( "heading_style_white", parent=heading_style, textColor=colors.white )
	doc = SimpleDocTemplate ( response, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch )
	
	data = [ ( "Bidder", Table ( [("ID", "Piece", "Bid", "Notes")], colWidths=[ 0.5*inch, 4.5*inch, 0.5*inch, 1.2*inch] ) ) ]

	for bidder in bidders:
		top_bids = bidder.top_bids()
		if top_bids:
			for i in range(0,len(top_bids),MAX_PIECES_PER_PAGE):
				bidder_data = []
				if i != 0:
					bidder_data.append ( ( Paragraph ( "... continued from previous page", normal_style ), "", "" ) )
				for bid in top_bids[i:i+MAX_PIECES_PER_PAGE]:
					bidder_data.append ( ( 
						bid.piece.code,
						Paragraph ("<i>%s</i>  by %s" % ( escape(bid.piece.name), 
								escape(bid.piece.artist.artistname()) ), normal_style ), 
						str(bid.amount), 
						bid.piece.voice_auction and "Voice Auction" or "" ) )
				if i + MAX_PIECES_PER_PAGE <= len(top_bids):
					bidder_data.append ( ( Paragraph ( "continued on next page...", normal_style ), "", "" ) )
				right_part = Table ( bidder_data, colWidths=[ 0.5*inch, 4.5*inch, 0.5*inch, 1.2*inch],
						style = [ 
								( "ROWBACKGROUNDS", (0,0), (-1,-1), ( colors.lightgrey, colors.white ) ),
								( "SIZE", (0,0), (0,-1), 8 ),
								( "ALIGN", (2,0), (2,-1), "DECIMAL" ),
								] )
				data.append ( ( 
					Paragraph ( ", ".join(["B"+str(x) for x in bidder.bidder_ids()]), heading_style_white ),
					right_part, 
					) )
		else:
			right_part = Table ( [[Paragraph ( "No winning bids", normal_style )]] )
			data.append ( ( 
					Paragraph ( ", ".join(["B"+str(x) for x in bidder.bidder_ids()]), heading_style_white ),
					right_part, 
					) )
				
	table_style = [
		( "LEFTPADDING", (1,0), (1,-1), 0 ),		
		( "RIGHTPADDING", (1,0), (1,-1), 0 ),		
		( "TOPPADDING", (1,0), (1,-1), 0 ),		
		( "BOTTOMPADDING", (1,0), (1,-1), 0 ),
		( "VALIGN", (0,0), (0,-1), "MIDDLE" ),
		( "BACKGROUND", (0,1), (0,-1), colors.black ),
		( "LINEABOVE", (0,1), (0,1), 2, colors.black ),
		( "LINEABOVE", (1,1), (0,-1), 2, colors.white ),
		( "LINEBELOW", (0,1), (0,-2), 2, colors.white ),
		( "LINEBELOW", (0,-1), (0,-1), 2, colors.black ),
		( "LINEABOVE", (1,1), (1,-1), 2, colors.black ),
		( "LINEBELOW", (1,1), (1,-1), 2, colors.black ),
		( "LINEABOVE", (0,'splitfirst'), (0,'splitfirst'), 2, colors.black ),
		( "LINEBELOW", (0,'splitlast'), (0,'splitlast'), 2, colors.black ),
		
		]	
	table = Table ( data, colWidths=[ 0.8*inch, 6.7*inch], repeatRows=1, style=table_style )
	story = [ table ]
	doc.build ( story )
	
	return response
	
@permission_required ( 'artshow.is_artshow_staff' )
def bid_entry_by_artist ( request ):

#	pieces = Piece.objects.filter ( status=Piece.StatusInShow ).order_by ( 'artist__artistid', 'pieceid' )
	pieces = Piece.objects.all().order_by ( 'artist__artistid', 'pieceid' )
	return bid_entry ( request, pieces )
	
	
@permission_required ( 'artshow.is_artshow_staff' )
def bid_entry_by_location ( request ):

#	pieces = Piece.objects.filter ( status=Piece.StatusInShow ).order_by ( 'location', 'artist__artistid', 'pieceid' )
	pieces = Piece.objects.all().order_by ( 'location', 'artist__artistid', 'pieceid' )
	return bid_entry ( request, pieces )
	
@permission_required ( 'artshow.is_artshow_staff' )
def bid_entry ( request, pieces ):
	
	response = HttpResponse ( mimetype="application/pdf" )

	styles = getSampleStyleSheet()	
	normal_style = styles["Normal"]
	heading_style = styles["Heading3"]
	heading_style_white = ParagraphStyle ( "heading_style_white", parent=heading_style, textColor=colors.white )
	doc = SimpleDocTemplate ( response, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch )
	
	data = [ ( "Loc.", "Artist", "Title", "Code", "Bidder", "Amount", "No\nSale", "Norm.\nSale", "Buy\nNow\nSale", "Voice\nAuct." ) ]
	
	for piece in pieces:
		data.append ( (
				Paragraph ( escape(piece.location), normal_style ),
				Paragraph ( escape(piece.artist.artistname()), normal_style ),
				Paragraph ( escape(piece.name), normal_style ),
				Paragraph ( escape(piece.code), normal_style ),
				"",
				"",
				"",
				"",
				"",
				"",
				) )
				
	table_style = [
		("GRID",(0,1),(-1,-1),0.5,colors.black),
		]	
	table = Table ( data, colWidths=[ 0.5*inch, 1.5*inch, 1.7*inch, 0.7*inch, 1*inch, 1*inch, 0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch ],
			repeatRows=1, style=table_style )
	story = [ table ]
	doc.build ( story )
	
	return response


#! /usr/bin/env python

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER, TA_LEFT, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.pagesizes import letter
from django.conf import settings
from models import Piece
from itertools import izip_longest
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from cgi import escape
import optparse

PIECES_PER_CONTROL_FORM = 20

default_style = ParagraphStyle ( "default_style", fontName="Helvetica", alignment=TA_CENTER, allowWidows=0, allowOrphans=0 )

left_align_style = ParagraphStyle ( "left_align_style", fontName="Helvetica", alignment=TA_LEFT, allowWidows=0, allowOrphans=0 )

barcode_style = ParagraphStyle ( "barcode_style", fontName="PrecisionID C39 04", alignment=TA_CENTER, allowWidows=0, allowOrphans=0 )



def draw_msg_into_frame ( frame, canvas, msg, font_size, min_font_size, style ):
	# From the largest to the smallest font sizes, try to flow the message
	# into the given frame.
	for size in range ( font_size, min_font_size-1, -1 ):
		current_style = ParagraphStyle ( "temp_style", parent=style, fontSize=size, leading=size )
		story = [ Paragraph ( escape(msg), current_style ) ]
		frame.addFromList ( story, canvas )
		if len(story) == 0: break  # Story empty, so all text was sucessfully flowed
	else:
	    # We've run out font sizing options, so clearly the story/text is too big to flow in.
		raise Exception ( "Could not flow text into box." )
		

def text_into_box ( canvas, msg, x0, y0, x1, y1, fontName="Helvetica", fontSize=24, minFontSize=6, units=inch, style=default_style ):
	frame = Frame ( x0*units, y0*units, (x1-x0)*units, (y1-y0)*units, leftPadding=2, rightPadding=2, topPadding=0, bottomPadding=4, showBoundary=0 )
	draw_msg_into_frame ( frame, canvas, msg, fontSize, minFontSize, style )
	

def generate_bidsheets_for_artists ( template_pdf, output, artists ):

	pieces = Piece.objects.filter ( artist__in=artists ).order_by ( 'artist__artistid', 'pieceid' )
	generate_bidsheets ( template_pdf, output, pieces )


def generate_bidsheets_fc ( template_pdf, output, pieces ):

	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont
	pdfmetrics.registerFont(TTFont('PrecisionID C39 04', 'artshow/files/PrecisionID C39 04.ttf'))

	c = Canvas(output,pagesize=letter)

	pdf = PdfReader ( template_pdf )
	xobj = pagexobj ( pdf.pages[0] )
	rlobj = makerl ( c, xobj )

	sheet_offsets = [
		(0,5.5),
		(4.25,5.5),
		(0,0),
		(4.25,0),
		]

	sheets_per_page = len(sheet_offsets)
	sheet_num = 0
	
	for piece in pieces:
	
		c.saveState ()
		c.translate ( sheet_offsets[sheet_num][0]*inch, sheet_offsets[sheet_num][1]*inch )
		c.doForm ( rlobj )
		
		c.saveState ()
		c.setLineWidth ( 4 )
		c.setFillColorRGB ( 1, 1, 1 )
		c.setStrokeColorRGB ( 1, 1, 1 )
		c.roundRect ( 1.1875*inch, 4.4375*inch, 1.75*inch, 0.5*inch, 0.0675*inch, stroke=True, fill=True )
		c.restoreState ()
		
		text_into_box ( c, u"*A"+unicode(piece.artist.artistid)+u"P"+unicode(piece.pieceid)+u"*", 1.3125, 4.6, 2.8125, 4.875, fontSize=14, style=barcode_style )
		
		text_into_box ( c, "Artist "+unicode(piece.artist.artistid), 1.25, 4.4375, 2.0, 4.625 )
		text_into_box ( c, "Piece "+unicode(piece.pieceid), 2.125, 4.4375, 2.875, 4.625 )
		text_into_box ( c, piece.artist.artistname(), 1.125, 4.125, 3.875, 4.375 )
		text_into_box ( c, piece.name, 0.75, 3.8125, 3.875, 4.0625 )
		text_into_box ( c, piece.media, 0.875, 3.5, 3.875, 3.75 )
		text_into_box ( c, piece.not_for_sale and "NFS" or unicode(piece.min_bid), 3.25, 2.625, 3.75, 3.0 )
		text_into_box ( c, piece.buy_now and unicode(piece.buy_now) or "N/A", 3.25, 1.9375, 3.75, 2.3125 )
		text_into_box ( c, "X", 3.375, 0.375, 3.5625, 0.675, style=left_align_style, fontSize=16 )		
			
		c.restoreState ()
		sheet_num += 1
		if sheet_num == sheets_per_page:
			c.showPage ()
			sheet_num = 0
				
	if sheet_num != 0:
		c.showPage ()
	c.save ()

	
def generate_bidsheets_vancoufur ( template_pdf, output, pieces ):

	c = Canvas(output,pagesize=letter)

	pdf = PdfReader ( template_pdf )
	xobj = pagexobj ( pdf.pages[0] )
	rlobj = makerl ( c, xobj )

	sheet_offsets = [
		(0,5.5),
		(4.25,5.5),
		(0,0),
		(4.25,0),
		]

	sheets_per_page = len(sheet_offsets)
	sheet_num = 0
	
	for piece in pieces:
	
		c.saveState ()
		c.translate ( sheet_offsets[sheet_num][0]*inch, sheet_offsets[sheet_num][1]*inch )
		c.doForm ( rlobj )
		
		text_into_box ( c, unicode(piece.artist.artistid), 2.6, 4.9, 3.2, 5.2 )
		text_into_box ( c, unicode(piece.pieceid), 3.3, 4.9, 3.9, 5.2 )
		text_into_box ( c, piece.artist.artistname(), 0.65, 4.1, 2.95, 4.5 )
		text_into_box ( c, piece.name, 0.65, 3.7, 2.95, 4.1 )
		text_into_box ( c, piece.media, 0.65, 3.32, 2.95, 3.7 )
		text_into_box ( c, piece.not_for_sale and "NFS" or unicode(piece.min_bid), 3.1, 4.1, 3.9, 4.35 )
		text_into_box ( c, piece.buy_now and unicode(piece.buy_now) or "N/A", 3.1, 3.7, 3.9, 3.95 )
		# text_into_box ( c, piece.not_for_sale and "NFS" or str(piece.min_bid), 3.1, 3.35, 3.9, 3.6 )
			
		c.restoreState ()
		sheet_num += 1
		if sheet_num == sheets_per_page:
			c.showPage ()
			sheet_num = 0
				
	if sheet_num != 0:
		c.showPage ()
	c.save ()

generate_bidsheets = generate_bidsheets_fc
	

def grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)
    
def yn ( b ):
	return "Y" if b else "N"
	
def priceornfs ( nfs, price ):
	return "NFS" if nfs else unicode(price)
	
def buynoworna ( price ):
	return "N/A" if price is None else unicode(price)


def generate_control_forms ( template_pdf, output, artists ):
	"""Write a pdf file to 'output' using 'template_pdf' as a template,
	and generate control forms (one or more pages each) for 'artists'.
	"""
	c = Canvas ( output, pagesize=letter )
	pdf = PdfReader ( template_pdf )
	xobj = pagexobj ( pdf.pages[0] )
	rlobj = makerl ( c, xobj )
	for artist in artists:
		pieces = artist.piece_set.order_by('pieceid')
		num_pieces = pieces.count()
		num_pages = (num_pieces + PIECES_PER_CONTROL_FORM - 1) // PIECES_PER_CONTROL_FORM
		for piecegroup in grouper ( PIECES_PER_CONTROL_FORM, pieces ):
			c.doForm ( rlobj )
			text_into_box ( c, settings.ARTSHOW_SHOW_YEAR, 2.4, 10.3, 3.05, 10.6 )
			text_into_box ( c, unicode(artist.artistid), 6.6, 10.25, 8.0, 10.5 )
			text_into_box ( c, artist.person.name, 1.7, 9.875, 4.1, 10.225, style=left_align_style )
			text_into_box ( c, artist.artistname(), 1.7, 9.5,    4.1, 9.85, style=left_align_style )
			text_into_box ( c, artist.person.address1 + " " + artist.person.address2, 1.7, 9.125,  4.1, 9.475, style=left_align_style )
			text_into_box ( c, artist.person.city, 1.7, 8.75,   4.1,  9.1, style=left_align_style   )
			text_into_box ( c, artist.person.state, 1.7, 8.375,  4.1,  8.725, style=left_align_style )
			text_into_box ( c, artist.person.postcode, 1.7, 8.0,    4.1,  8.35, style=left_align_style  )
			text_into_box ( c, artist.person.country, 1.7, 7.625,  4.1,  7.975, style=left_align_style )
			text_into_box ( c, artist.person.phone, 1.7, 7.25,   4.1,  7.6, style=left_align_style   )
			text_into_box ( c, artist.person.email, 4.9, 9.875, 8.0, 10.225, style=left_align_style, fontSize=16 )		
			text_into_box ( c, ", ".join ( [agent.name for agent in artist.agents.all()] ), 5.9, 7.625, 8.0, 7.975, style=left_align_style )
			for i, piece in enumerate(piecegroup):
				if piece is None: continue
				y0 = 6.45 - i*0.25
				y1 = 6.675 - i*0.25
				text_into_box ( c, unicode(piece.pieceid), 0.5, y0, 1.0, y1 )			
				text_into_box ( c, piece.name, 1.0, y0, 4.0, y1, style=left_align_style )			
				text_into_box ( c, yn(piece.adult), 4.0, y0, 4.5, y1 )			
				text_into_box ( c, priceornfs(piece.not_for_sale,piece.min_bid), 4.5, y0, 5.25, y1 )			
				text_into_box ( c, buynoworna(piece.buy_now), 5.25, y0, 6.0, y1 )			
			c.showPage ()
		
	c.save ()
		
		
		
		
		
		
		
		
	
	


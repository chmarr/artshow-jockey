#! /usr/bin/env python

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER, TA_LEFT, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.pagesizes import letter

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from cgi import escape

import optparse

default_style = ParagraphStyle ( "default_style", fontName="Helvetica", alignment=TA_CENTER, allowWidows=0, allowOrphans=0 )
left_align = ParagraphStyle ( "left_align", fontName="Helvetica", alignment=TA_LEFT, allowWidows=0, allowOrphans=0 )


def draw_msg_into_frame ( frame, canvas, msg, font_size, min_font_size, style=default_style ):
	# From the largest to the smallest font sizes, try to flow the message
	# into the given frame.
	msg = escape(msg)
	msg = msg.replace('\n','<br/>')
	for size in range ( font_size, min_font_size-1, -1 ):
		current_style = ParagraphStyle ( "temp_style", parent=style, fontSize=size, leading=size )
		story = [ Paragraph ( msg, current_style ) ]
		frame.addFromList ( story, canvas )
		if len(story) == 0: break  # Story empty, so all text was sucessfully flowed
	else:
	    # We've run out font sizing options, so clearly the story/text is too big to flow in.
		raise Exception ( "Could not flow text into box." )
		

def text_into_box ( canvas, msg, x0, y0, x1, y1, fontName="Helvetica", fontSize=18, minFontSize=6, units=inch, style=default_style ):
	frame = Frame ( x0*units, y0*units, (x1-x0)*units, (y1-y0)*units, leftPadding=2, rightPadding=2, topPadding=0, bottomPadding=4, showBoundary=0 )
	draw_msg_into_frame ( frame, canvas, msg, fontSize, minFontSize, style=style )
	

def generate_bidsheets_for_artists ( template_pdf, output, artists ):

	pieces = Piece.objects.filter ( artist__in=artists ).order_by ( 'artist__artistid', 'pieceid' )
	generate_bidsheets ( template_pdf, output, pieces )
	
	
def generate_bidsheets ( template_pdf, output, pieces ):

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
		
		text_into_box ( c, str(piece.artist.artistid), 2.6, 4.9, 3.2, 5.2 )
		text_into_box ( c, str(piece.pieceid), 3.3, 4.9, 3.9, 5.2 )
		text_into_box ( c, piece.artist.artistname(), 0.65, 4.1, 2.95, 4.5 )
		text_into_box ( c, piece.name, 0.65, 3.7, 2.95, 4.1 )
		text_into_box ( c, piece.media, 0.65, 3.32, 2.95, 3.7 )
		text_into_box ( c, piece.not_for_sale and "NFS" or str(piece.min_bid), 3.1, 4.1, 3.9, 4.35 )
		text_into_box ( c, piece.buy_now and str(piece.buy_now) or "X", 3.1, 3.7, 3.9, 3.95 )
		# text_into_box ( c, piece.not_for_sale and "NFS" or str(piece.min_bid), 3.1, 3.35, 3.9, 3.6 )
			
		c.restoreState ()
		sheet_num += 1
		if sheet_num == sheets_per_page:
			c.showPage ()
			sheet_num = 0
				
	if sheet_num != 0:
		c.showPage ()
	c.save ()
	

def generate_mailing_labels ( output, artists ):

	c = Canvas(output,pagesize=letter)
	
	label_number = 0
	
	for artist in artists:
		column = label_number%3
		row = label_number/3
		c.saveState ()
		c.translate ( 3/16.0*inch + column*(2+3/4.0)*inch, (9+1/2.0)*inch - row*inch )
		text_into_box ( c, artist.person.get_mailing_label(), 0.1, 0.0, 2.5, 0.85, fontSize=14, style=left_align )
		c.restoreState ()
		
		label_number += 1
		if label_number == 30:
			c.showPage ()
			label_number = 0
			
	if label_number != 0:
		c.showPage ()
	c.save ()

#! /usr/bin/env python

from django.conf import settings
from models import Piece

preprint = __import__ ( settings.ARTSHOW_PREPRINT_MODULE, globals(), locals(), ['bid_sheets','control_forms','piece_stickers','mailing_labels'] )

def generate_bidsheets_for_artists ( template_pdf, output, artists ):
	pieces = Piece.objects.filter ( artist__in=artists ).order_by ( 'artist__artistid', 'pieceid' )
	preprint.bid_sheets ( pieces, output )
	

def generate_bidsheets ( template_pdf, output, pieces ):
    preprint.bid_sheets ( pieces, output )
    

def generate_mailing_labels ( output, artists ):
    preprint.mailing_labels ( artists, output )


def generate_control_forms ( template_pdf, output, artists ):
	"""Write a pdf file to 'output' using 'template_pdf' as a template,
	and generate control forms (one or more pages each) for 'artists'.
	"""
	pieces = Piece.objects.filter ( artist__in=artists ).order_by ( 'artist__artistid','pieceid' )
	preprint.control_forms ( pieces, output )
		
	
def generate_piece_stickers ( output, pieces ):
    preprint.piece_stickers ( pieces, output )

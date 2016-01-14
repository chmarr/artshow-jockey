#! /usr/bin/env python

from .conf import settings
from .models import Piece

preprint = __import__(settings.ARTSHOW_PREPRINT_MODULE, globals(), locals(),
                      ['bid_sheets', 'control_forms', 'piece_stickers', 'mailing_labels', 'artist_quickref_stickers'])


def generate_bidsheets_for_artists(output, artists):
    pieces = Piece.objects.filter(artist__in=artists).order_by('artist__artistid', 'pieceid')
    preprint.bid_sheets(pieces, output)


def generate_bidsheets(output, pieces):
    preprint.bid_sheets(pieces, output)


def generate_mailing_labels(output, artists):
    preprint.mailing_labels(artists, output)


def generate_control_forms(output, artists):
    pieces = Piece.objects.filter(artist__in=artists).order_by('artist__artistid', 'pieceid')
    preprint.control_forms(pieces, output)


def generate_control_forms_for_pieces(output, pieces):
    preprint.control_forms(pieces, output)


def generate_piece_stickers(output, pieces):
    preprint.piece_stickers(pieces, output)


def generate_artist_quickref_stickers(output, artists):
    preprint.artist_quickref_stickers(artists, output)

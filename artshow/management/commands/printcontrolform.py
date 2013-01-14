from django.core.management.base import BaseCommand, CommandError
from artshow.models import *
from optparse import make_option
from artshow import control_form_dmp
import sys

class Command ( BaseCommand ):

	args = 'artistid ... '
	help = "Generate LQ570 code for control forms"
		
	def handle ( self, *args, **options ):
		artist_ids = [ int(x) for x in args ]
		for id in artist_ids:
			try:
				artist = Artist.objects.get(artistid=id)
			except Artist.DoesNotExist:
				print >>sys.stderr, "Artist with ID %d does not exist" % id
				continue
				
			if artist.piece_set.count() == 0:
				print >>sys.stderr, "Artist %s has no pieces. Not printing." % artist
				continue
				
			control_form_dmp.generate_lq570 ( artist, sys.stdout )

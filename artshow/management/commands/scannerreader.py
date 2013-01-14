from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from artshow.models import BatchScan
from optparse import make_option
import datetime
import select

	
class Command ( BaseCommand ):

	args = ''
	help = "Monitor connected scanner"
	
	option_list = BaseCommand.option_list + (
		make_option ( "--device", type="string", action="append", default=settings.ARTSHOW_SCANNER_DEVICE, help="scanner device name [%default]"),
		)
	
	def handle ( self, *args, **options ):
		device = options['device']
		f = open ( device )
		
		while True:
			data = []
			print "waiting for new data"
			l = f.readline ()
			print "\a"
			while True:
				if not l:
					print "oops. no data to read. wtf?"
				l = l.strip()
				if l:
					data.append ( l )
				print l
				rlist, wlist, xlist = select.select ( [f], [], [f], 5.0 )
				if not rlist and not xlist:
					break
				l = f.readline ()
			print "timed out"
			print "\a"
			data_str = "\n".join ( data ) + "\n"
			batchscan = BatchScan ( data=data, date_scanned=datetime.datetime.now() )
			batchscan.save ()
			print str(batchscan), "saved"
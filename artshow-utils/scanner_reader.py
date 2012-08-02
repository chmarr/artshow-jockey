#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import BatchScan
import optparse, datetime
import select

def load_batchscan ( data ):
	batchscan = BatchScan ( data=data, date_scanned=datetime.datetime.now() )
	batchscan.save ()

f = open ( "/dev/ttyUSB0" )

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
	load_batchscan ( data_str )
	

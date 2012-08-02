#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import BatchScan
import optparse, datetime

def load_batchscan ( filename ):
	data = open(filename).read()
	batchscan = BatchScan ( data=data, date_scanned=datetime.datetime.now() )
	batchscan.save ()

def get_options ():
	parser = optparse.OptionParser ()
	opts, args = parser.parse_args ()
	opts.file = args[0]
	return opts

if __name__ == "__main__":
	opts = get_options ()
	load_batchscan ( opts.file )

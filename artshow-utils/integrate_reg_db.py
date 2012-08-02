#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from artshow.models import Bidder
import optparse, csv

class NameDoesntMatch ( Exception ): pass


def integrate_reg_entry ( entry ):

	try:
		bidder = Bidder.objects.get ( regid = entry['badge_id'] )
	except Bidder.DoesNotExist:
		try: 
			bidder = Bidder.objects.get ( regid = entry['badge_id'].replace('-','') )
		except Bidder.DoesNotExist:
			return

	print "Artshow DB:", bidder.name, bidder.bidder_ids()
	print "Reg DB:", entry['real_name'], entry['badge_id']
	if bidder.name != entry['real_name']:
		print "names dont match"
		while True:
			i = raw_input ( "1) use Artshow DB name  2) use Reg DB name  3) reject" )
			if i == "1":
				real_name = bidder.name
				break
			elif i == "2":
				real_name = entry['real_name']
				break
			elif i == "3":
				real_name = None
				break
	else:
		real_name = bidder.name
	
	if real_name != None:
		bidder.name = real_name
		bidder.address1 = entry.get('address1','')
		bidder.address2 = entry.get('address2','')
		bidder.city = entry.get('city','')
		bidder.state = entry.get('state','')
		bidder.postcode = entry.get('postcode','')
		bidder.country = entry.get('country','')
		bidder.email = entry.get('email','')
		bidder.phone = entry.get('phone','')
		bidder.save ()
		print "saved"
		print
	else:
		print "rejected"
		print
		raise NameDoesntMatch


def integrate_reg_db ( regfile, rejects_file=None ):

	f = open(regfile)
	c = csv.DictReader(f)
	
	if rejects_file:
		rf = open(rejects_file,"w")
		rejects = csv.DictWriter(rf,['badge_id','real_name','fan_name','address1','address2','city','state','postcode','country','email','phone'])
	else:
		rejects = None

	for entry in c:
		try:
			integrate_reg_entry ( entry )
		except (Bidder.DoesNotExist,NameDoesntMatch):
			if rejects:
				rejects.writerow ( entry )

	if rejects:
		rf.close ()


def get_options ():
	parser = optparse.OptionParser ()
	parser.add_option ( "--rejects-file", type="str", default=None )
	opts, args = parser.parse_args ()
	opts.regfile = args[0]
	return opts

def main ():
	opts = get_options ()
	integrate_reg_db ( opts.regfile, rejects_file=opts.rejects_file )

if __name__ == "__main__":
	main ()


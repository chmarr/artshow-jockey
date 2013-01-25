#! /usr/bin/env python
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

"""This piece of crap code is intended for Further Confusion to be able to integrate the separate
registration database into the Person model by matching up registration IDs and, if the names
are different, giving the option of selecting one name over the other. As is this is probably
only useful for Further Confusion, but can be the basis of a local solution.

Remember to set PYTHONPATH and DJANGO_SETTINGS_MODULE variables before running.

It has _NOT_ been updated to support the new peeps.Person model yet."""

cli_defaults = {
	'rejects-file': None,
	}
	
cli_usage = "%prog [options] input-file"
cli_description = """\
Integrate information from another database to help complete missing fields.
"""

from artshow.models import Person, Bidder
import optparse, csv

class NameDoesntMatch ( Exception ): pass


def integrate_reg_entry ( entry ):

	badge_id = entry['UID']+"-"+entry['FC2013_reg_num']

	try:
		person = Person.objects.get ( reg_id = badge_id )
	except Bidder.DoesNotExist:
		try: 
			person = Person.objects.get ( reg_id = badge_id.replace('-','') )
		except Person.DoesNotExist:
			return
			
	real_name = entry['rl_first'] + " " + entry['rl_last']
	real_name = real_name.strip()
	
	print "Artshow DB:", person.name, person.bidder.bidder_ids()
	print "Reg DB:", real_name, badge_id
	if person.name != real_name:
		print "names dont match"
		while True:
			i = raw_input ( "1) use Artshow DB name  2) use Reg DB name  3) reject" )
			if i == "1":
				real_name = person.name
				break
			elif i == "2":
				real_name = real_name
				break
			elif i == "3":
				real_name = None
				break
	else:
		real_name = person.name
	
	if real_name != None:
		person.name = real_name
		person.address1 = entry.get('Address 1 Line 1','')
		person.address2 = entry.get('Address 1 Line 2','')
		person.city = entry.get('Address 1 City','')
		person.state = entry.get('Address 1 State','')
		person.postcode = entry.get('Address 1 Zip','')
		person.country = ''
		person.email = entry.get('EMail 1','')
		person.save ()
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
		rejects = csv.writer ( rf )
		rejects.writerow ( c.fieldnames )
	else:
		rejects = None

	for entry in c:
		try:
			integrate_reg_entry ( entry )
		except (Person.DoesNotExist,Bidder.DoesNotExist,NameDoesntMatch):
			if rejects:
				rejects.writerow ( entry )

	if rejects:
		rf.close ()


def get_options ():
	parser = optparse.OptionParser ( usage=cli_usage, description=cli_description )
	parser.set_defaults ( **cli_defaults )
	parser.add_option ( "--rejects-file", type="str", help="File for rejects [%default]" )
	opts, args = parser.parse_args ()
	try:
		opts.regfile = args[0]
	except IndexError:
		raise parser.error ( "missing argument" )
	return opts

def main ():
	opts = get_options ()
	integrate_reg_db ( opts.regfile, rejects_file=opts.rejects_file )

if __name__ == "__main__":
	main ()


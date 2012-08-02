#! /usr/bin/env python26
# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

# TODO: Handle setting DJANGO environment variable

import optparse, subprocess
from django.template import Template, Context
from artshow.models import Artist
from artshow.email1 import make_email
import sqlite3

default_db = "data/artshowproj.db"
default_wrap_cols = 79

def send_email ( data, test=False ):
	
	if test:
		print data
		print "-----------"
	else:
		p = subprocess.Popen ( ("/usr/lib/sendmail", "-t"), stdin=subprocess.PIPE )
		p.stdin.write ( data )
		p.stdin.close ()
		print "sent email"


def get_template ( db, template_name ):
	cur = db.cursor ()
	cur.execute ( "select template from artshow_emailtemplate where name=? limit 1", ( template_name, ) )
	row = cur.fetchone ()
	if row == None:
		raise KeyError ( "email template %s not found" % template_name )
	return row[0]

def get_artist_ids ( db, ids, filters ):

	cur = db.cursor ()
	if filters:
		cur.execute ( "create temporary table filters ( id int, state bool )" )
		for f_str in filters:
			checkoff,state = f_str.split("=")
			state = {"yes":True,"no":False}[state.lower()]
			cur.execute ( "insert into filters values ( (select id from artshow_checkoff where name=? or shortname=?), ? )", ( checkoff, checkoff, state ) )
		cur.execute ( """
create temporary table match_list as
select artshow_artist.id as artist_id, count(positive_checkoffs.checkoff_id) as positive_matches, count(negative_checkoffs.checkoff_id) as negative_matches from artshow_artist
left join ( select artshow_artist_checkoffs.artist_id as artist_id, artshow_artist_checkoffs.checkoff_id as checkoff_id from artshow_artist_checkoffs join filters on artshow_artist_checkoffs.checkoff_id=filters.id where filters.state=?) as negative_checkoffs on artshow_artist.id=negative_checkoffs.artist_id
left join ( select artshow_artist_checkoffs.artist_id as artist_id, artshow_artist_checkoffs.checkoff_id as checkoff_id from artshow_artist_checkoffs join filters on artshow_artist_checkoffs.checkoff_id=filters.id where filters.state=?) as positive_checkoffs on artshow_artist.id=positive_checkoffs.artist_id
group by artshow_artist.id
having positive_matches=(select count(*) from filters where state=?) and negative_matches=0
""", ( False, True, True ) )
	else:
		cur.execute ( "create temporary table match_list as select artshow_artist.id as artist_id from artshow_artist" )

	if ids == "active":
		cur.execute ( "select artshow_artist.id from artshow_artist join match_list on artshow_artist.id=match_list.artist_id where ( select sum(requested) from artshow_allocation where artist_id = artshow_artist.id) > 0" ) 
	elif ids == "showing":
		cur.execute ( "select artshow_artist.id from artshow_artist join match_list on artshow_artist.id=match_list.artist_id where ( select sum(allocated) from artshow_allocation where artist_id = artshow_artist.id) > 0" ) 
	elif ids == "all":
		cur.execute ( "select artshow_artist.id from artshow_artist join match_list on artshow_artist.id=match_list.artist_id" )
	else:
		cur.execute ( "create temporary table temp_ids ( id int )" )
		for id in ids:
			cur.execute ( "insert into temp_ids values (?)", ( id, ) )
		cur.execute ( "select artshow_artist.id from artshow_artist where artistid in temp_ids" )

	while True:
		row = cur.fetchone()
		if row==None: break
		yield row[0]


def send_emails ( template_name, db_name, ids=None, cols=default_wrap_cols, test=False, filters=[] ):
	db = sqlite3.connect ( db_name )
	template_str = get_template ( db, template_name )
	for artist_id in get_artist_ids ( db, ids, filters ):
		artist_obj = Artist.objects.get(id=artist_id)
		email = make_email ( artist_obj, template_str, cols=cols )
		send_email ( email, test=test )


def get_opts ():
	parser = optparse.OptionParser ()
	parser.add_option ( "--test", default=False, action="store_true" )
	parser.add_option ( "--db", default=default_db )
	parser.add_option ( "--ids", default="active", type="str" )
	parser.add_option ( "--cols", type="int", default=default_wrap_cols )
	parser.add_option ( "--filter", action="append", default=[] )
	opts, args = parser.parse_args ()
	if opts.ids not in ( "active", "showing", "all" ):
		s1 = opts.ids.split(',')
		opts.ids = [ int(x) for x in s1 ]
	opts.template = args[0]
	return opts


if __name__ == "__main__":
	opts = get_opts ()
	send_emails ( opts.template, opts.db, ids=opts.ids, cols=opts.cols, test=opts.test, filters=opts.filter )

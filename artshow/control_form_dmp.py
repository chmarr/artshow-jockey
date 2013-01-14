from django.conf import settings
from itertools import izip_longest

PIECES_PER_CONTROL_FORM = 20

def auto_compress ( s, std_width ):

	s = str(s)

	if len(s) <= std_width-2:
		return " %-*s " % ( std_width-2, s )

	compressed_width, extras = divmod ( (std_width*5), 3 )
	# Extras is how many 60ths of an inch to add, will only be 0, 1 or 2

	# Condensed, Cancel Condensed
	data = "\x0f %-*s \x12" % ( compressed_width-2, s )
	if extras:
		# Set Relative Horizontal Print Position, in 1/180ths (in LQ mode)
		data += "\x1b\\" + chr(extras*3) + chr(0)

	return data
	
	
def grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

	

def generate_lq570 ( artist, data ):

	for piecegroup in grouper ( PIECES_PER_CONTROL_FORM, artist.piece_set.all() ):
	
		data.write ( "\x1b0" ) # Set 1/8 inch spacing
		data.write ( "\x1bM" ) # Set 12 CPI
	
		# Lines 1-4 
		for i in range(2):
			data.write ( "\n" )
	
		# Line 5
		# \x0e \x14 double width printing on/off
		# \x1b E \x1b F bold on/off
		data.write ( "%26s%s%43s\x0e\x1bE%s\x1bF\x14\n" % ( " ", auto_compress ( settings.ARTSHOW_SHOW_YEAR, 9 ), " ", str(artist.artistid) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 8
		data.write ( "%17s%s%12s%s\n" % ( " ", auto_compress ( artist.person.name, 27 ), " ", auto_compress ( artist.person.email, 36 ) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 11
		data.write ( "%17s%s\n" % ( " ", auto_compress ( artist.artistname(), 27 ) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 14
		data.write ( "%17s%s\n" % ( " ", auto_compress ( " ".join([artist.person.address1,artist.person.address2]), 27 ) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 17
		data.write ( "%17s%s\n" % ( " ", auto_compress ( artist.person.city, 27 ) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 20
		data.write ( "%17s%s\n" % ( " ", auto_compress ( artist.person.state, 27 ) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 23
		data.write ( "%17s%s\n" % ( " ", auto_compress ( artist.person.postcode, 27 ) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 26
		data.write ( "%17s%s\n" % ( " ", auto_compress ( artist.person.country, 27 ) ) )
		data.write ( "\n" )
		data.write ( "\n" )
	
		# Line 29
		data.write ( "%17s%s\n" % ( " ", auto_compress ( artist.person.phone, 27 ) ) )
	
		# Line 30-35
		for i in range(6):
			data.write ( "\n" )
	
		# Line 36-95
		for piece in piecegroup:
			if piece is not None:
				# \x1bE and \x1bF = Bold on/off
				data.write ( "    %4d %s   %s   %7s  %7s\n" % ( piece.pieceid, auto_compress ( piece.name, 36 ), piece.adult and "\x1bEY\x1bF" or "N", 
					piece.min_bid and ("%7d"%piece.min_bid) or "  NFS  ", 
					piece.buy_now and ("%7d"%piece.buy_now) or "  N/A  " ) )
				data.write ( "\n" )
	
		data.write ( "\x0c" ) # Form Feed



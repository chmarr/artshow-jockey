#! /usr/bin/env python

cli_defaults = {
	}
cli_usage = "%prog infile"
cli_description = """\
Read in a PDF file and overlay a 0.1" grid on top of it. Writes to stdout.
"""

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, TA_CENTER, ParagraphStyle
from reportlab.platypus import Paragraph, Frame

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

import optparse, sys

def grid_overlay ( infile ):
	
	c = Canvas ( sys.stdout )

	pdf = PdfReader ( infile )
	xobj = pagexobj ( pdf.pages[0] )
	rlobj = makerl ( c, xobj )

	sheet_offsets = [
		(0,5.5),
		(4.25,5.5),
		(0,0),
		(4.25,0),
		]

	sheets_per_page = len(sheet_offsets)
	sheet_num = 0
	
	c.doForm ( rlobj )
	
	xmax = 90
	ymax = 115
	
	dinch = inch * 0.1
	
	thickline = 0.5
	thinline = 0.1
	
	for x in range(0,xmax):
		if x % 10 == 0:
			c.setLineWidth ( thickline )
		else:
			c.setLineWidth ( thinline )
		c.line ( x*dinch, 0, x*dinch, ymax*dinch )

	for y in range(0,ymax):		
		if y % 10 == 0:
			c.setLineWidth ( thickline )
		else:
			c.setLineWidth ( thinline )
		c.line ( 0, y*dinch, xmax*dinch, y*dinch )
			
	c.showPage ()
	c.save ()
	
	
def get_options ():
	parser = optparse.OptionParser ( usage=cli_usage, description=cli_description )
	parser.set_defaults ( **cli_defaults )
	opts, args = parser.parse_args ()
	try:
		opts.file = args[0]
	except IndexError:
		raise parser.error ( "Missing argument" )
	return opts
	
if __name__ == "__main__":
	opts = get_options ()
	grid_overlay ( opts.file )

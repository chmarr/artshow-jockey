#! /usr/bin/env python

"""Modify a PDF file by overlaying a 0.1" grid upon it.

Useful to construct text overlay boxes for printing to existing PDF forms.
"""

cli_defaults = {
    'lpi': 10,
}
cli_usage = "%prog infile"
cli_description = """\
Read in a PDF file and overlay a 0.1" grid on top of it. Writes to stdout.
"""

import optparse
import sys

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl


def grid_overlay(infile, outfile=sys.stdout, pagesize=letter, lpi=10):
    """Read PDF file 'infile'. Generates a new PDF file to 'outfile'
    containing the first page (only) of infile, with a 'lpi' grid
    overlaid.
    """

    c = Canvas(outfile, pagesize=pagesize)

    pdf = PdfReader(infile)
    xobj = pagexobj(pdf.pages[0])
    rlobj = makerl(c, xobj)

    c.doForm(rlobj)

    xmax = 9
    ymax = 12

    thickline = 0.5
    thinline = 0.1

    for x in range(0, xmax):
        c.setLineWidth(thickline)
        for xx in range(0, lpi):
            x0 = (x + (float(xx) / lpi)) * inch
            c.line(x0, 0, x0, ymax * inch)
            c.setLineWidth(thinline)

    for y in range(0, ymax):
        c.setLineWidth(thickline)
        for yy in range(0, lpi):
            y0 = (y + (float(yy) / lpi)) * inch
            c.line(0, y0, xmax * inch, y0)
            c.setLineWidth(thinline)

    c.showPage()
    c.save()


def get_options():
    parser = optparse.OptionParser(usage=cli_usage, description=cli_description)
    parser.set_defaults(**cli_defaults)
    parser.add_option("--lpi", type="int", help="lines per inch [%default]")
    opts, args = parser.parse_args()
    try:
        opts.file = args[0]
    except IndexError:
        raise parser.error("Missing argument")
    return opts


if __name__ == "__main__":
    opts = get_options()
    grid_overlay(opts.file, lpi=opts.lpi)

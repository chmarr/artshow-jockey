from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.platypus import Frame, Paragraph
import cgi


def escape(s):
    s = cgi.escape(s)
    # For some reason the layout will eat the first char if its a space or &nbsp;, so we add another one in.
    if s[0:1] == " ":
        s = " " + s
    s = s.replace(' ', '&nbsp;')
    return s


def text_to_pdf(text, output, lines_per_page=66):
    c = Canvas(output, pagesize=letter)
    style = ParagraphStyle ( "default_style", fontName="Courier-Bold", fontSize=10, leading=11.1, alignment=TA_LEFT, allowWidows=1, allowOrphans=1 )
    lines = text.splitlines()
    while lines:
        group = lines[:lines_per_page]
        lines = lines[lines_per_page:]
        newtext = "<br/>".join ( escape(l) for l in group )
        story = [Paragraph(newtext, style)]
        f = Frame(0.5*inch, 0.25*inch, 7.5*inch, 10.5*inch)
        f.addFromList(story, c)
        assert len(story) == 0
        c.showPage()
    c.save()

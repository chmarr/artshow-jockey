from cgi import escape as escape_html

from reportlab.lib.units import inch
from reportlab.lib.styles import TA_CENTER, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .conf import settings


pdfmetrics.registerFont(TTFont(*settings.ARTSHOW_BARCODE_FONT))

default_style = ParagraphStyle("default", fontName="Helvetica", fontSize=18, leading=18,
                               alignment=TA_CENTER, allowWidows=0, allowOrphans=0)


def squeeze_text_into_box(canvas, text, x0, y0, x1, y1, units=inch, style=default_style, escape=True):
    if escape:
        text = escape_html(text).replace('\n', '<br/>')
    frame = Frame(x0 * units, y0 * units, (x1 - x0) * units, (y1 - y0) * units, leftPadding=2, rightPadding=2,
                  topPadding=0, bottomPadding=4, showBoundary=0)
    current_style = style
    current_size = style.fontSize
    while True:
        story = [Paragraph(text, current_style)]
        frame.addFromList(story, canvas)
        if len(story) == 0:
            break  # Story empty, so all text was successfully flowed into frame
        if current_size > 6:
            current_size -= 1
        elif current_size > 3:
            current_size -= 0.5
        elif current_size > 1:
            current_size -= 0.1
        else:
            raise Exception("Could not squeeze text into box, even with a font size of 1 point.")
        current_style = ParagraphStyle("temp_style", parent=style, fontSize=current_size, leading=current_size)


def load_pdf_as_form(canvas, path):
    """
    Convert a pdf file into a reportlab object

    :param canvas: Reportlab Canvas object the form may be written to
    :param path: path to pdf file to open
    :return: a reportlab object that may be drawn using canvas.doForm(obj)
    """
    pdf = PdfReader(path)
    xobj = pagexobj(pdf.pages[0])
    reportlab_obj = makerl(canvas, xobj)
    return reportlab_obj

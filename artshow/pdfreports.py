# Artshow Jockey
# Copyright (C) 2009, 2010 Chris Cogdon
# See file COPYING for licence details

from cgi import escape
from decimal import Decimal

from django.db.models import Min
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import LETTER
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from reportlab.lib.sequencer import getSequencer
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, Frame, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from .models import *
from .conf import settings


MAX_PIECES_PER_PAGE = 30


@permission_required('artshow.is_artshow_staff')
def winning_bidders(request):
    bidders = Bidder.objects.all().annotate(first_bidderid=Min('bidderid')).order_by('first_bidderid')
    response = HttpResponse(mimetype="application/pdf")

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    heading_style = styles["Heading3"]
    heading_style_white = ParagraphStyle("heading_style_white", parent=heading_style, textColor=colors.white)
    doc = SimpleDocTemplate(response, leftMargin=0.5 * inch, rightMargin=0.5 * inch, topMargin=0.5 * inch,
                            bottomMargin=0.5 * inch)

    data = [("Bidder",
             Table([("ID", "Piece", "Bid", "Notes")], colWidths=[0.5 * inch, 4.5 * inch, 0.5 * inch, 1.2 * inch]))]

    for bidder in bidders:
        top_bids = bidder.top_bids()
        if top_bids:
            for i in range(0, len(top_bids), MAX_PIECES_PER_PAGE):
                bidder_data = []
                if i != 0:
                    bidder_data.append((Paragraph("... continued from previous page", normal_style), "", ""))
                for bid in top_bids[i:i + MAX_PIECES_PER_PAGE]:
                    bidder_data.append((
                        bid.piece.code,
                        Paragraph("<i>%s</i>  by %s" % (escape(bid.piece.name),
                                                        escape(bid.piece.artist.artistname())),
                                  normal_style),
                        str(bid.amount),
                        bid.piece.voice_auction and "Voice Auction" or ""))
                if i + MAX_PIECES_PER_PAGE <= len(top_bids):
                    bidder_data.append((Paragraph("continued on next page...", normal_style), "", ""))
                right_part = Table(bidder_data, colWidths=[0.5 * inch, 4.5 * inch, 0.5 * inch, 1.2 * inch],
                                   style=[
                                       ("ROWBACKGROUNDS", (0, 0), (-1, -1), ( colors.lightgrey, colors.white)),
                                       ("SIZE", (0, 0), (0, -1), 8),
                                       ("ALIGN", (2, 0), (2, -1), "DECIMAL"),
                                   ])
                data.append((
                    Paragraph(", ".join(["B" + str(x) for x in bidder.bidder_ids()]), heading_style_white),
                    right_part,
                ))
        else:
            right_part = Table([[Paragraph("No winning bids", normal_style)]])
            data.append((
                Paragraph(", ".join(["B" + str(x) for x in bidder.bidder_ids()]), heading_style_white),
                right_part,
            ))

    table_style = [
        ("LEFTPADDING", (1, 0), (1, -1), 0),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (1, 0), (1, -1), 0),
        ("BOTTOMPADDING", (1, 0), (1, -1), 0),
        ("VALIGN", (0, 0), (0, -1), "MIDDLE"),
        ("BACKGROUND", (0, 1), (0, -1), colors.black),
        ("LINEABOVE", (0, 1), (0, 1), 2, colors.black),
        ("LINEABOVE", (1, 1), (0, -1), 2, colors.white),
        ("LINEBELOW", (0, 1), (0, -2), 2, colors.white),
        ("LINEBELOW", (0, -1), (0, -1), 2, colors.black),
        ("LINEABOVE", (1, 1), (1, -1), 2, colors.black),
        ("LINEBELOW", (1, 1), (1, -1), 2, colors.black),
        ("LINEABOVE", (0, 'splitfirst'), (0, 'splitfirst'), 2, colors.black),
        ("LINEBELOW", (0, 'splitlast'), (0, 'splitlast'), 2, colors.black),

    ]
    table = Table(data, colWidths=[0.8 * inch, 6.7 * inch], repeatRows=1, style=table_style)
    story = [table]
    doc.build(story)

    return response


@permission_required('artshow.is_artshow_staff')
def bid_entry_by_artist(request):

#	pieces = Piece.objects.filter ( status=Piece.StatusInShow ).order_by ( 'artist__artistid', 'pieceid' )
    pieces = Piece.objects.all().order_by('artist__artistid', 'pieceid')
    return bid_entry(request, pieces)


@permission_required('artshow.is_artshow_staff')
def bid_entry_by_location(request):

#	pieces = Piece.objects.filter ( status=Piece.StatusInShow ).order_by ( 'location', 'artist__artistid', 'pieceid' )
    pieces = Piece.objects.all().order_by('location', 'artist__artistid', 'pieceid')
    return bid_entry(request, pieces)


@permission_required('artshow.is_artshow_staff')
def bid_entry(request, pieces):
    response = HttpResponse(mimetype="application/pdf")

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    heading_style = styles["Heading3"]
    heading_style_white = ParagraphStyle("heading_style_white", parent=heading_style, textColor=colors.white)
    doc = SimpleDocTemplate(response, leftMargin=0.5 * inch, rightMargin=0.5 * inch, topMargin=0.5 * inch,
                            bottomMargin=0.5 * inch)

    data = [("Loc.", "Artist", "Title", "Code", "Bidder", "Amount", "No\nSale", "Norm.\nSale", "Buy\nNow\nSale",
             "Voice\nAuct.")]

    for piece in pieces:
        data.append((
            Paragraph(escape(piece.location), normal_style),
            Paragraph(escape(piece.artist.artistname()), normal_style),
            Paragraph(escape(piece.name), normal_style),
            Paragraph(escape(piece.code), normal_style),
            "",
            "",
            "",
            "",
            "",
            "",
        ))

    table_style = [
        ("GRID", (0, 1), (-1, -1), 0.5, colors.black),
    ]
    table = Table(data,
                  colWidths=[0.5 * inch, 1.5 * inch, 1.7 * inch, 0.7 * inch, 1 * inch, 1 * inch, 0.4 * inch, 0.4 * inch,
                             0.4 * inch, 0.4 * inch],
                  repeatRows=1, style=table_style)
    story = [table]
    doc.build(story)

    return response


_quantization_value = Decimal(10) ** -settings.ARTSHOW_MONEY_PRECISION


def format_money(value):
    return unicode(value.quantize(_quantization_value))


def draw_invoice_header(canvas, doc, invoice, purpose):
    normal_style = ParagraphStyle("normal", fontName="Helvetica")
    frame = Frame(0.75 * inch, doc.pagesize[1] - 1.75 * inch,
                  doc.pagesize[0] - 1.5 * inch, 1 * inch,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    invoice_info_data = [
        ["Invoice", settings.ARTSHOW_INVOICE_PREFIX + str(invoice.id)],
        ["Page", Paragraph('<para align="right"><seq id="pageno" /></para>', normal_style)],
        ["Date", invoice.paid_date.strftime("%b %d, %Y")],
        ["Reg ID", invoice.payer.person.reg_id],
        ["Bidder IDs",
         Paragraph("<para align=right><b>" + escape(" ".join(invoice.payer.bidder_ids())) + "</b></para>",
                   normal_style)],
    ]
    invoice_info_style = [
        #("GRID", (0,0), (-1,-1), 0.1, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONT", (1, 0), (1, 0), "Helvetica-Bold"),
        ("FONT", (1, 4), (1, 4), "Helvetica-Bold"),
    ]
    invoice_info_table = Table(invoice_info_data, colWidths=[0.75 * inch, 1.5 * inch], style=invoice_info_style)
    header_data = [
        [settings.ARTSHOW_SHOW_NAME + " - " + settings.ARTSHOW_SHOW_YEAR, invoice_info_table],
        [purpose + "\n    " + invoice.payer.name()],
    ]
    header_table_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.1, colors.black),
        ("SPAN", (1, 0), (1, -1)),
        ("LEFTPADDING", (1, 0), (1, 0), 0),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (1, 0), (1, 0), 3),
        ("BOTTOMPADDING", (1, 0), (1, 0), 3),
    ]
    header_table = Table(header_data, colWidths=[4.75 * inch, 2.25 * inch], style=header_table_style)
    header_story = [header_table, Spacer(inch, 0.25 * inch)]
    frame.addFromList(header_story, canvas)


def invoice_to_pdf(invoice, outf):
    normal_style = ParagraphStyle("normal", fontName="Helvetica")
    piece_condition_style = ParagraphStyle("piececondition", normal_style, fontSize=normal_style.fontSize - 2,
                                           leading=normal_style.leading - 2)
    piece_details_style = ParagraphStyle("pieceseller", piece_condition_style)

    def invoice_header(canvas, doc):
        draw_invoice_header(canvas, doc, invoice, "Invoice for:")

    doc = SimpleDocTemplate(outf, pagesize=LETTER,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=1.75 * inch, bottomMargin=0.75 * inch,
                            onFirstPage=invoice_header, onLaterPages=invoice_header)

    story = []

    body_data = [["Code", "Description", "Amount (" + settings.ARTSHOW_MONEY_CURRENCY + ")"]]

    num_items = 0
    for item in invoice.invoiceitem_set.order_by("piece__artist__artistid", "piece__pieceid"):
        num_items += 1
        piece = item.piece
        paragraphs = [Paragraph("<i>" + escape(piece.name) + u"</i> \u2014 by " + escape(piece.artistname()), normal_style)]
        details_body_parts = [escape(piece.media)]
        if piece.condition:
            details_body_parts.append(escape(piece.condition))
        if piece.other_artist:
            details_body_parts.append(escape("sold by " + piece.artist.artistname()))
        paragraphs.append(Paragraph(u" \u2014 ".join(details_body_parts), piece_details_style))
        body_data.append([item.piece.code, paragraphs, format_money(item.price)])

    if invoice.tax_paid:
        subtotal_row = len(body_data)
        body_data.append(["", "Subtotal", format_money(invoice.item_total())])
        body_data.append(["", settings.ARTSHOW_TAX_DESCRIPTION, format_money(invoice.tax_paid)])
    else:
        subtotal_row = None

    total_row = len(body_data)
    body_data.append(["", str(num_items) + u" items \u2014 Total Due", format_money(invoice.item_and_tax_total())])

    body_data.append(["", "", ""])

    for payment in invoice.invoicepayment_set.all():
        body_data.append(["", payment.get_payment_method_display(), format_money(payment.amount)])

    body_data.append(["", "Total Paid", unicode(invoice.total_paid())])

    body_table_style = [
        ("FONTSIZE", (0, 0), (-1, 0), normal_style.fontSize - 4),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("LEADING", (0, 0), (-1, 0), normal_style.leading - 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("ALIGN", (1, total_row), (1, -1), "RIGHT"),
        ("FONT", (2, total_row), (2, total_row), "Helvetica-Bold"),
        ("FONT", (2, -1), (2, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0,0), (-1, -1), 0.1, colors.black),
        ("LINEABOVE", (0, total_row), (-1, total_row), 0.75, colors.black),
        ("LINEABOVE", (0, -1), (-1, -1), 0.75, colors.black),
    ]

    if subtotal_row is not None:
        body_table_style.append(("ALIGN", (1, subtotal_row), (1, subtotal_row + 1), "RIGHT"))
        body_table_style.append(("LINEABOVE", (0, subtotal_row), (-1, subtotal_row), 0.75, colors.black))

    body_table = Table(body_data, colWidths=[0.75 * inch, 5.0 * inch, 1.25 * inch], style=body_table_style,
                       repeatRows=1)
    story.append(body_table)

    # TODO - Figure out a better way of handling this horrible hack.
    # "Paragraph" does not use the sequencer inside the Document, but instead the global sequencer :(
    getSequencer().reset("pageno", 0)

    doc.build(story, onFirstPage=invoice_header, onLaterPages=invoice_header)


@permission_required('artshow.is_artshow_staff')
def pdf_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    response = HttpResponse(mimetype="application/pdf")
    invoice_to_pdf(invoice, response)
    return response


def picklist_to_pdf(invoice, outf):
    normal_style = ParagraphStyle("normal", fontName="Helvetica")
    piece_condition_style = ParagraphStyle("piececondition", normal_style, fontSize=normal_style.fontSize - 2,
                                           leading=normal_style.leading - 2)
    piece_details_style = ParagraphStyle("pieceseller", piece_condition_style)

    def invoice_header(canvas, doc):
        draw_invoice_header(canvas, doc, invoice, "Pick-List for:")

    doc = SimpleDocTemplate(outf, pagesize=LETTER,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=1.75 * inch, bottomMargin=0.75 * inch,
                            onFirstPage=invoice_header, onLaterPages=invoice_header)

    story = []

    body_data = [
        ["Loc.", "Code", u"\u2714", "Description", "Amount", u"\u2714"],
        [Paragraph('<para align="right">Confirm Bidder ID on each sheet</para>', normal_style),"","","","",u"[ ]"],
    ]

    num_items = 0
    for item in invoice.invoiceitem_set.order_by("piece__location", "piece__artist__artistid", "piece__pieceid"):
        num_items += 1
        piece = item.piece
        paragraphs = [Paragraph("<i>" + escape(piece.name) + u"</i> \u2014 by " + escape(piece.artistname()), normal_style)]
        details_body_parts = [escape(piece.media)]
        if piece.condition:
            details_body_parts.append(escape(piece.condition))
        if piece.other_artist:
            details_body_parts.append(escape("sold by " + piece.artist.artistname()))
        paragraphs.append(Paragraph(u" \u2014 ".join(details_body_parts), piece_details_style))
        body_data.append([piece.location, piece.code, u"[ ]", paragraphs,
                          Paragraph("<para align=\"right\"><b>"+escape(str(item.price))+"</b></para>",
                                    normal_style),
                          u"[ ]"])

    body_data.append([Paragraph('<para align="right">Confirm <b>%s</b> items, <b>%s</b> '
                                'bid-sheets, then initial</para>' % (num_items, num_items),
                                normal_style), "", "", "", "", "__"])

    body_table_style = [
        ("FONTSIZE", (0, 0), (-1, 0), normal_style.fontSize - 4),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("LEADING", (0, 0), (-1, 0), normal_style.leading - 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (4, 0), (4, -1), "RIGHT"),
        ("SPAN",(0,1),(4,1)),
        ("SPAN",(0,num_items+2),(4,num_items+2)),
        ("LINEBELOW", (0,0), (-1, -1), 0.1, colors.black),
        #("GRID", (0,0), (-1,-1), 0.1, colors.black),
    ]

    body_table = Table(body_data, colWidths=[0.5 * inch, 0.75 * inch, 0.25 * inch, 4.25 * inch, 1 * inch, 0.25 * inch],
                       style=body_table_style,
                       repeatRows=1)
    story.append(body_table)
    story.append(Spacer(0.25*inch, 0.25*inch))

    signature_block = KeepTogether([
        Paragraph(escape("I, %s, or a duly authorized agent, acknowledge receiving the above "
                                      "%d items." % (invoice.payer.name(), num_items)), normal_style),
        Spacer(0.25*inch, 0.25*inch),
        Paragraph("Signature _______________________________________________", normal_style),
        Spacer(0.25*inch, 0.25*inch),
        Paragraph("Agent Name _______________________________________________", normal_style),
    ])
    story.append(signature_block)


    # TODO - Figure out a better way of handling this horrible hack.
    # "Paragraph" does not use the sequencer inside the Document, but instead the global sequencer :(
    getSequencer().reset("pageno", 0)

    doc.build(story, onFirstPage=invoice_header, onLaterPages=invoice_header)


@permission_required('artshow.is_artshow_staff')
def pdf_picklist(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    response = HttpResponse(mimetype="application/pdf")
    picklist_to_pdf(invoice, response)
    return response

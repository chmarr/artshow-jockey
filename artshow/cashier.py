# Artshow Jockey
# Copyright (C) 2009, 2010, 2011 Chris Cogdon
# See file COPYING for licence details
from StringIO import StringIO
import subprocess
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from .models import Bidder, Piece, InvoicePayment, InvoiceItem, Invoice
from django import forms
from django.db.models import Q
from django.forms import ModelForm
from django.forms.models import modelformset_factory, BaseModelFormSet
from .conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
import logging
import datetime
from . import invoicegen
from . import pdfreports
logger = logging.getLogger(__name__)
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
import json
from .conf import _DISABLED as SETTING_DISABLED, _UNCONFIGURED as SETTING_UNCONFIGURED


class BidderSearchForm (forms.Form):
    text = forms.CharField(label="Search Text")


@permission_required('artshow.add_invoice')
def cashier(request):
    search_executed = False
    if request.method == "POST":
        form = BidderSearchForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            # TODO - the following will return multiple entries for name base if bidder has two IDs
            bidders = Bidder.objects.filter(Q(person__name__icontains=text) | Q(bidderid__id=text))
            search_executed = True
        else:
            bidders = []
    else:
        form = BidderSearchForm()
        bidders = []

    c = {"form": form, "bidders": bidders, "search_executed": search_executed}
    return render(request, 'artshow/cashier.html', c)


class ItemsForm (forms.Form):
    tax_paid = forms.DecimalField()


class PaymentForm (ModelForm):
    class Meta:
        model = InvoicePayment
        fields = ("amount", "payment_method", "notes")
        widgets = {'amount': forms.HiddenInput, 'payment_method': forms.HiddenInput, 'notes': forms.HiddenInput}

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise ValidationError("amount must be greater than 0")
        return amount


class PaymentFormSet (BaseModelFormSet):
    def clean(self):
        total = sum([form.cleaned_data['amount'] for form in self.forms], Decimal(0))
        # self.items_total is set from the cashier_bidder function.
        if total != self.items_total:
            raise ValidationError("payments (%s) must equal invoice total (%s)" % (total, self.items_total))


PaymentFormSet = modelformset_factory(InvoicePayment, form=PaymentForm, formset=PaymentFormSet, extra=0)


class SelectPieceForm (forms.Form):
    select = forms.BooleanField(required=False)


# TODO probably need a @transaction.commit_on_success here

@permission_required('artshow.add_invoice')
def cashier_bidder(request, bidder_id):

    bidder = get_object_or_404(Bidder, pk=bidder_id)

    all_bids = bidder.top_bids(unsold_only=True)
    available_bids = []
    pending_bids = []
    bid_dict = {}
    for bid in all_bids:
        if bid.piece.status == Piece.StatusWon:
            available_bids.append(bid)
            bid_dict[bid.pk] = bid
        else:
            pending_bids.append(bid)

    if request.method == "POST":
        for bid in available_bids:
            form = SelectPieceForm(request.POST, prefix="bid-%d" % bid.pk)
            bid.form = form
        items_form = ItemsForm(request.POST, prefix="items")
        payment_formset = PaymentFormSet(request.POST, prefix="payment", queryset=InvoicePayment.objects.none())
        if all(bid.form.is_valid() for bid in available_bids) and items_form.is_valid():

            logger.debug("Bids and Items Form passed")

            selected_bids = [bid for bid in available_bids if bid.form.cleaned_data['select']]

            if len(selected_bids) == 0:
                items_form._errors['__all__'] = items_form.error_class(["Invoice must contain at least one item"])
            else:
                subtotal = sum([bid.amount for bid in selected_bids], Decimal(0))
                tax_paid = items_form.cleaned_data['tax_paid']
                total = subtotal + tax_paid

                payment_formset.items_total = total
                if payment_formset.is_valid():

                    logger.debug("payment formset passed")

                    invoice = Invoice(payer=bidder, tax_paid=tax_paid, paid_date=datetime.datetime.now(),
                                      created_by=request.user)
                    invoice.save()
                    payments = payment_formset.save(commit=False)
                    for payment in payments:
                        payment.invoice = invoice
                        payment.save()
                    for bid in selected_bids:
                        invoice_item = InvoiceItem(piece=bid.piece, price=bid.amount, invoice=invoice)
                        invoice_item.save()
                        bid.piece.status = Piece.StatusSold
                        bid.piece.save()

                    if settings.ARTSHOW_AUTOPRINT_INVOICE:
                        do_print_invoices(request, invoice.id, settings.ARTSHOW_AUTOPRINT_INVOICE)

                    return redirect(cashier_invoice, invoice_id=invoice.id)
    else:
        for bid in available_bids:
            form = SelectPieceForm(prefix="bid-%d" % bid.pk, initial={"select": False})
            bid.form = form
        items_form = ItemsForm(prefix="items")
        payment_formset = PaymentFormSet(prefix="payment", queryset=InvoicePayment.objects.none())

    payment_types = dict(InvoicePayment.PAYMENT_METHOD_CHOICES[1:])
    payment_types_json = json.dumps ( payment_types, sort_keys=True )

    tax_rate = settings.ARTSHOW_TAX_RATE
    money_precision = settings.ARTSHOW_MONEY_PRECISION

    c = dict(bidder=bidder, available_bids=available_bids, pending_bids=pending_bids, items_form=items_form,
             payment_formset=payment_formset, payment_types=payment_types, payment_types_json=payment_types_json,
             tax_rate=tax_rate, money_precision=money_precision)

    return render(request, 'artshow/cashier_bidder.html', c)

@permission_required('artshow.add_invoice')
def cashier_bidder_invoices(request, bidder_id):

    bidder = get_object_or_404(Bidder, pk=bidder_id)
    invoices = Invoice.objects.filter(payer=bidder).order_by('id')
    return render(request, 'artshow/cashier_bidder_invoices.html',
                  {'bidder': bidder, 'invoices': invoices, 'money_precision': settings.ARTSHOW_MONEY_PRECISION})


@permission_required('artshow.add_invoice')
def cashier_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    print_invoice_form = PrintInvoiceForm()

    c = dict(invoice=invoice, money_precision=settings.ARTSHOW_MONEY_PRECISION, tax_rate=settings.ARTSHOW_TAX_RATE,
             tax_description=settings.ARTSHOW_TAX_DESCRIPTION,
             invoice_prefix=settings.ARTSHOW_INVOICE_PREFIX, print_invoice_form=print_invoice_form)

    return render(request, 'artshow/cashier_invoice.html', c)


class PrintInvoiceForm (forms.Form):
    return_to = forms.CharField(required=False, widget=forms.HiddenInput)
    customer = forms.BooleanField(label="Customer", required=False)
    merchant = forms.BooleanField(label="Merchant", required=False)
    picklist = forms.BooleanField(label="Pick List", required=False)


# def do_print_invoices(request, invoice_id, copy_names):
#     try:
#         invoicegen.print_invoices([invoice_id], copy_names, to_printer=True)
#     except invoicegen.PrintingError, x:
#         messages.error(request, "Printing failed. Please ask administrator to consult error log")
#         logger.error("Printing failed with exception: %s", x)
#     else:
#         messages.info(request, "Invoice %s has been sent to the printer" % invoice_id)


def do_print_invoices2(invoice, copy_names):

    for copy_name in copy_names:
        do_print_invoices3(invoice, copy_name)


def do_print_invoices3(invoice, copy_name):

    sbuf = StringIO()

    try:
        if copy_name == "PICK LIST":
            print_command = (settings.ARTSHOW_PICKLIST_PRINT_COMMAND
                             if settings.ARTSHOW_PICKLIST_PRINT_COMMAND != SETTING_UNCONFIGURED
                             else settings.ARTSHOW_PRINT_COMMAND)
            pdfreports.picklist_to_pdf(invoice, sbuf)
        else:
            print_command = settings.ARTSHOW_PRINT_COMMAND
            pdfreports.invoice_to_pdf(invoice, sbuf)
    except Exception, x:
        logger.error("Could not generate invoice: %s", x)
        raise invoicegen.PrintingError ("Could not generate invoice: %s" % x)

    if not sbuf.getvalue():
        logger.error("nothing to generate")
    else:
        if print_command is SETTING_DISABLED:
            logger.error("Cannot print invoice. ARTSHOW_PRINT_COMMAND is DISABLED")
            raise invoicegen.PrintingError("Printing is DISABLED in configuration")
        p = subprocess.Popen(print_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        output, error = p.communicate(sbuf.getvalue())
        if output:
            logger.debug("printing command returned: %s", output)
        if error:
            logger.error("printing command returned error: %s", error)
            raise invoicegen.PrintingError(error)


def do_print_invoices(request, invoice_id, copy_names):
    invoice = Invoice.objects.get(id=invoice_id)
    try:
        do_print_invoices2(invoice, copy_names)
    except invoicegen.PrintingError, x:
        messages.error(request, "Printing failed. Please ask administrator to consult error log")
        logger.error("Printing failed with exception: %s", x)
    else:
        messages.info(request, "Invoice %s has been sent to the printer" % invoice_id)


@permission_required('artshow.add_invoice')
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if request.method == "POST":
        form = PrintInvoiceForm(request.POST)
        if form.is_valid():
            copy_names = []
            if form.cleaned_data['customer']:
                copy_names.append("CUSTOMER COPY")
            if form.cleaned_data['merchant']:
                copy_names.append("MERCHANT COPY")
            if form.cleaned_data['picklist']:
                copy_names.append("PICK LIST")
            do_print_invoices(request, invoice.id, copy_names)
            return_to = form.cleaned_data['return_to']
            if not return_to:
                return_to = "artshow.views.index"
            return redirect(return_to)

    messages.error(request, "Print Invoice request is invalid")
    return HttpResponseBadRequest("Print Invoice request is invalid.")

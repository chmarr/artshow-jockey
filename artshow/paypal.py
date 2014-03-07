from decimal import Decimal
from urllib import urlopen
from urlparse import parse_qs
import datetime
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.dispatch import Signal, receiver
from django.http import HttpResponse
from django.utils.http import urlencode
from .conf import settings
from logging import getLogger
from django.views.decorators.csrf import csrf_exempt
from artshow.models import Payment

paypal_logger = getLogger("paypal")


# Example URL
# https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=sales%40internetwonders.com&undefined_quantity=0&
# item_name=Art+Show+Payment&item_number=12345-123124134&amount=23&shipping=0&no_shipping=1&return=internetwonders.com&
# cancel_return=internetwonders.com&currency_code=USD&bn=PP%2dBuyNowBF&cn=&charset=UTF%2d8

def make_paypal_url(request, payment):

    signer = Signer()
    item_number = signer.sign(unicode(payment.id))

    params = {"cmd": "_xclick",
              "business": settings.ARTSHOW_PAYPAL_ACCOUNT,
              "undefined_quantity": "0",
              "item_name": "Art Show Payment from " + payment.artist.artistname(),
              "item_number": item_number,
              "amount": unicode(payment.amount),
              "shipping": "0",
              "no_shipping": "1",
              "return": request.build_absolute_uri(reverse("artshow.manage.payment_made_paypal",
                                                           args=(payment.artist_id,))),
              "cancel_return": request.build_absolute_uri(
                  reverse("artshow.manage.payment_cancelled_paypal",
                          args=(payment.artist_id,)) + "?" + urlencode({"item_number": item_number})),
              "currency_code": "USD",
              "bn": "PP-BuyNow",
              "charset": "UTF-8",
              "notify_url": request.build_absolute_uri(reverse(ipn_handler)),
              }

    return settings.ARTSHOW_PAYPAL_URL + "?" + urlencode(params)


ipn_received = Signal(providing_args=["query"])


class IPNProcessingError(Exception):
    pass


@receiver(ipn_received)
def process_ipn(sender, **kwargs):

    query = kwargs['query']
    payment_id = None

    try:
        verify_url = settings.ARTSHOW_PAYPAL_URL + "?cmd=_notify-validate&" + query
        paypal_logger.debug("requesting verification from: %s", verify_url)
        pipe = urlopen(verify_url)
        text = pipe.read(128)

        if text != "VERIFIED":
            raise IPNProcessingError("Paypal returned %s for verification" % text)

        params = parse_qs(query)
        paypal_logger.info("validated PayPal IPN: %s", repr(params))

        txn_type = params['txn_type'][0]
        if txn_type != "web_accept":
            raise IPNProcessingError("txn_type is %s not web_accept" % txn_type)

        item_number = params['item_number'][0]
        payment_status = params['payment_status'][0]
        amount_gross = params['mc_gross'][0]
        amount_gross = Decimal(amount_gross)
        payer_email = params['payer_email'][0]
        payment_date = params['payment_date'][0]

        # PayPal uses dates in this format: HH:MM:SS Mmm DD, YYYY PDT
        payment_date = datetime.datetime.strptime(payment_date, "%H:%M:%S %b %d, %Y PDT")

        if payment_status != "Completed":
            raise IPNProcessingError("payment status is %s != Completed" % payment_status)

        signer = Signer()
        payment_id = signer.unsign(item_number)
        payment = Payment.objects.get(id=payment_id)

        if payment.payment_type_id != settings.ARTSHOW_PAYMENT_PENDING_PK:
            if payment.payment_type_id == settings.ARTSHOW_PAYMENT_RECEIVED_PK and payment.amount == amount_gross:
                paypal_logger.info("additional notification received for payment id %s. this is normal", payment_id)
                return
            raise IPNProcessingError("payment is not Payment Pending state")

        if payment.amount != amount_gross:
            paypal_logger.warning("payment is being changed from %s to %s", payment.amount, amount_gross)

        paypal_logger.info("marking payment received. payment id: %s  amount: %s  paypal email: %s",
                           payment_id, amount_gross, payer_email)

        payment.amount = amount_gross
        payment.payment_type_id = settings.ARTSHOW_PAYMENT_RECEIVED_PK
        payment.description = "Paypal " + payer_email
        payment.date = payment_date
        payment.save()

    except Exception, x:
        paypal_logger.error("Error when getting validation for: %s", query)
        if payment_id:
            paypal_logger.error("... during processing of payment_id: %s", payment_id)
        paypal_logger.error("%s", x)


@csrf_exempt
def ipn_handler(request):

    if request.method == "POST":
        query_string = request.body
    else:
        query_string = request.META['QUERY_STRING']

    paypal_logger.debug("received IPN notification with query: %s ", query_string)
    ipn_received.send(None, query=query_string)

    return HttpResponse("", mimetype="text/plain")

from urllib import urlopen
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.dispatch import Signal, receiver
from django.http import HttpResponse
from django.utils.http import urlencode, urlunquote_plus
from django.conf import settings
from logging import getLogger

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
              "return": request.build_absolute_uri(reverse("artshow.manage.payment_made_paypal", args=(payment.artist_id,))),
              "cancel_return": request.build_absolute_uri(reverse("artshow.manage.payment_cancelled_paypal",
                                       args=(payment.artist_id,)) + "?" + urlencode({"item_number": item_number})),
              "currency_code": "USD",
              "bn": "PP-BuyNow",
              "charset": "UTF-8",
              "notify_url": request.build_absolute_uri(reverse(ipn_handler)),
    }

    return settings.ARTSHOW_PAYPAL_URL + "?" + urlencode(params)


ipn_received = Signal(providing_args=["query"])


@receiver(ipn_received)
def process_ipn(sender, **kwargs):

    query = kwargs['query']

    def log_query_for_error():
        paypal_logger.error("Error when getting validation for: %s", query)

    verify_url = settings.ARTSHOW_PAYPAL_URL + "?cmd=_notify-validate&" + query
    paypal_logger.debug("requesting verification from: %s", verify_url)
    try:
        pipe = urlopen(verify_url)
        text = pipe.read(128)
    except Exception, x:
        log_query_for_error()
        paypal_logger.error("error getting verification: %s", str(x))
        return

    if text != "VERIFIED":
        log_query_for_error()
        paypal_logger.error("PayPal returned %s for verification", text)
        return

    params = urlunquote_plus(query)
    paypal_logger.info("received PayPal IPN. params: %s", repr(params))

    # TODO do the fancy processing here.
    # Find the relevant Payemnt using the item number
    # ensure that the type is "Payment Pending"
    # switch it to "Payment received", adjust the amount, set the comment field, update the timestamp, and save.


def ipn_handler(request):

    query_string = request.META['QUERY_STRING']

    paypal_logger.debug("received IPN notification with query: %s ", query_string)
    ipn_received.send(None, query=query_string)

    return HttpResponse("", mimetype="text/plain")















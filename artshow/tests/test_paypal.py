from .. import paypal
import datetime
from django.utils import timezone
from django.test import TestCase

class PayPalTests (TestCase):
    def test_date_processing(self):
        self.assertEqual(paypal.convert_date("10:10:10 Jun 10, 2000 PST"),
                         datetime.datetime(2000,06,10,10,10,10,tzinfo=paypal.pstzone))
        self.assertEqual((paypal.convert_date("10:10:10 Jun 10, 2000 PST") - datetime.datetime(1970,1,1,tzinfo=timezone.utc)).total_seconds(), 960660610 )
        self.assertEqual(paypal.convert_date("10:10:10 Jun 10, 2000 PDT"),
                         datetime.datetime(2000,06,10,10,10,10,tzinfo=paypal.pdtzone))
        self.assertEqual((paypal.convert_date("10:10:10 Jun 10, 2000 PDT") - datetime.datetime(1970,1,1,tzinfo=timezone.utc)).total_seconds(), 960657010 )
        self.assertRaises(ValueError, paypal.convert_date, "Thu Mar  6 23:27:40 PST 2014")
        self.assertRaises(ValueError, paypal.convert_date, "10:10:10 Jun 10, 2000 GMT")

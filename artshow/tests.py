import datetime
from django.test import TestCase
from .utils import artshow_settings
from .conf import settings
from . import mod11codes
from . import paypal
from django.utils import timezone


class AttributeFilterTest (TestCase):
    def test_passed_access(self):
        self.assertEqual(artshow_settings.SITE_NAME, settings.SITE_NAME)
        self.assertEqual(artshow_settings.SITE_ROOT_URL, settings.SITE_ROOT_URL)
        self.assertEqual(artshow_settings.ARTSHOW_SHOW_YEAR, settings.ARTSHOW_SHOW_YEAR)

    def test_failed_access(self):
        def get_secret_key():
            return artshow_settings.SECRET_KEY
        self.assertRaisesRegexp(AttributeError,
                                "AttributeFilter blocked access to 'SECRET_KEY'.*",
                                get_secret_key)


class Mod11Test (TestCase):
    def test_generation(self):
        self.assertEqual(mod11codes.make_check("196"), "1")
        self.assertEqual(mod11codes.make_check("197"), "X")
        self.assertEqual(mod11codes.make_check("197", check10="@"), "@")
        self.assertEqual(mod11codes.make_check("197", offset=4), "3")

    def test_check_passes(self):
        self.assertIsNone(mod11codes.check("1961"))
        self.assertIsNone(mod11codes.check("197X"))
        self.assertIsNone(mod11codes.check("197@", check10="@"))
        self.assertIsNone(mod11codes.check("1973", offset=4))

    def test_check_failures(self):
        self.assertRaises(mod11codes.CheckDigitError, mod11codes.check, "196X")
        self.assertRaises(mod11codes.CheckDigitError, mod11codes.check, "1970")
        self.assertRaises(mod11codes.CheckDigitError, mod11codes.check, "197X", check10="@")
        self.assertRaises(mod11codes.CheckDigitError, mod11codes.check, "197X", offset=4)


class PayPalTests (TestCase):
    def test_date_processing(self):
        self.assertEqual(paypal.convert_date("10:10:10 Jun 10, 2000 PST"),
                         datetime.datetime(2000,06,10,10,10,10,tzinfo=paypal.pstzone))
        self.assertEqual((paypal.convert_date("10:10:10 Jun 10, 2000 PST") - datetime.datetime(1970,1,1,tzinfo=timezone.utc)).total_seconds(), 960660610 )
        self.assertEqual(paypal.convert_date("10:10:10 Jun 10, 2000 PDT"),
                         datetime.datetime(2000,06,10,10,10,10,tzinfo=paypal.pdtzone))
        self.assertEqual((paypal.convert_date("10:10:10 Jun 10, 2000 PDT") - datetime.datetime(1970,1,1,tzinfo=timezone.utc)).total_seconds(), 960657010 )

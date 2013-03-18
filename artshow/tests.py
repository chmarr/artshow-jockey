from django.test import TestCase
from artshow.utils import artshow_settings
from django.conf import settings


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

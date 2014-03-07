from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordResetForm
from . import captcha


class ReCaptchaField(forms.CharField):
    default_error_messages = {
        'captcha_invalid': _(u'Invalid captcha')
    }

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptchaWidget
        self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        check_captcha = captcha.submit(recaptcha_challenge_value,
                                       recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.ValidationError(self.error_messages['captcha_invalid'])
        return values[0]


class ReCaptchaWidget(forms.widgets.Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        return mark_safe(u'%s' % captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY, use_ssl=True))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None),
                data.get(self.recaptcha_response_name, None)]


class CaptchaPasswordResetForm(PasswordResetForm):
    recaptcha = ReCaptchaField()

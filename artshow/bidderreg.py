from StringIO import StringIO
import subprocess
from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib.formtools.wizard.views import CookieWizardView
from django.shortcuts import render, redirect
from .conf import settings
from artshow.models import Person, Bidder, BidderId
import logging
logger = logging.getLogger(__name__)
from .conf import _DISABLED as SETTING_DISABLED


preprint = __import__(settings.ARTSHOW_PREPRINT_MODULE, globals(), locals(),
                      ['bidder_agreement'])


class BidderRegistrationForm0(forms.Form):
    pass


class BidderRegistrationForm1(forms.Form):
    name = forms.CharField(max_length=100,
                           help_text="Your real, first and last name. This should match your identification.")
    reg_id = forms.CharField(max_length=20,
                             help_text="The number on the front of your convention badge. It looks like 123-456, and may have fewer or more digits. Enter the dash, too.")
    cell_contact = forms.CharField(max_length=40, required=False,
                                   help_text="If you have one, provide your cell number or that of a friend.")
    other_contact = forms.CharField(max_length=100, required=False,
                                    help_text="Optionally, another way to contact you during the convention, such as your hotel and room number.")
    details_changed = forms.BooleanField(initial=False, required=False,
                                         help_text="When you registered at the convention, you provided your address and e-mail. Have these changed since then?")

    def clean(self):
        cleaned_data = super(BidderRegistrationForm1, self).clean()
        cell_contact = cleaned_data.get("cell_contact")
        other_contact = cleaned_data.get("other_contact")
        if cell_contact == "" and other_contact == "":
            raise forms.ValidationError("Please enter at least one way to contact you at the show.")
        reg_id = cleaned_data.get("reg_id")
        if not settings.ARTSHOW_REGID_NONUNIQUE:
            matched_people = Person.objects.filter(reg_id=reg_id)
            if BidderId.objects.filter(bidder__person__in=matched_people).exists():
                raise forms.ValidationError(
                    "We think you have already been issued a Bidder ID. If this is unexpected, please see Staff immediately")
        return cleaned_data


class BidderRegistrationForm2(forms.Form):
    address1 = forms.CharField(max_length=100, required=False)
    address2 = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=40, required=False)
    postcode = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=40, required=False)
    phone = forms.CharField(max_length=40, required=False)
    email = forms.CharField(max_length=100, required=False)


# noinspection PyUnusedLocal
def do_print_bidder_registration_form(bidder):

    sbuf = StringIO()
    preprint.bidder_agreement(bidder, sbuf)

    if settings.ARTSHOW_PRINT_COMMAND is SETTING_DISABLED:
        logger.error("Cannot print agreement. ARTSHOW_PRINT_COMMAND is DISABLED")
        raise Exception("Printing is DISABLED in configuration")
    p = subprocess.Popen(settings.ARTSHOW_PRINT_COMMAND, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)
    output, error = p.communicate(sbuf.getvalue())
    if output:
        logger.debug("printing command returned: %s", output)
    if error:
        logger.error("printing command returned error: %s", error)
        raise Exception(error)


class BidderRegistrationWizard(CookieWizardView):
    template_name = "artshow/bidderreg_wizard.html"

    def done(self, form_list, **kwargs):

        p = b = None
        for form in form_list:
            cleaned_data = form.cleaned_data
            if isinstance(form, BidderRegistrationForm1):
                p = Person(
                    name=cleaned_data['name'],
                    reg_id=cleaned_data['reg_id'],
                )
                cell_contact = cleaned_data.get('cell_contact', '')
                other_contact = cleaned_data.get('other_contact', '')
                at_con_contact = "\n".join((x for x in [cell_contact, other_contact] if x))
                b = Bidder(at_con_contact=at_con_contact)
            elif isinstance(form, BidderRegistrationForm2):
                p.address1 = cleaned_data.get('address1', '')
                p.address2 = cleaned_data.get('address2', '')
                p.city = cleaned_data.get('city', '')
                p.state = cleaned_data.get('state', '')
                p.postcode = cleaned_data.get('postcode', '')
                p.country = cleaned_data.get('country', '')
                p.phone = cleaned_data.get('phone', '')
                p.email = cleaned_data.get('email', '')
        if b is None:
            raise forms.ValidationError("End of wizard without creating bidder.")
        if p is None:
            raise forms.ValidationError("End of wizard without creating person.")
        p.save()
        b.person = p
        b.save()
        do_print_bidder_registration_form(b)
        return redirect(final)

@permission_required('artshow.is_artshow_kiosk')
def final(request):
    return render(request, "artshow/bidderreg_final.html")


def process_step_2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('1') or {}
    return cleaned_data.get('details_changed', False)

# permission is applied in urls.py
bidderreg_wizard_view = BidderRegistrationWizard.as_view(
    [BidderRegistrationForm0, BidderRegistrationForm1, BidderRegistrationForm2],
    condition_dict={'2': process_step_2})

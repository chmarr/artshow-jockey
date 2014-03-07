from django import forms
from .conf import settings
from django.db.models import Q
from .models import Person, Artist, ArtistAccess
from django.contrib.auth.models import User
from django.shortcuts import render
from .utils import create_user_from_email, send_password_reset_email
from .forms import ArtistRegisterForm, LongerTextInput


class AgreementForm(forms.Form):
    electronic_signature = \
        forms.CharField(required=True,
                        help_text="You must read and agree to our <a href=\"%s\" target=\"_blank\">"
                                  "Artist Agreement</a>. "
                                  "Please type in your full name here as your \"electronic signature\"." %
                                  settings.ARTSHOW_ARTIST_AGREEMENT_URL,
                        widget=LongerTextInput)

class PersonForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Real Name", help_text="Your real, legal name", widget=LongerTextInput)
    address1 = forms.CharField(required=True, label="Postal Address",
                               help_text="Address where we can send paper correspondence", widget=LongerTextInput)
    address2 = forms.CharField(required=False, label="Apt, Suite, etc.", widget=LongerTextInput)
    city = forms.CharField(required=True, widget=LongerTextInput)
    state = forms.CharField(required=True, label="State/Province", widget=LongerTextInput)
    postcode = forms.CharField(required=True, label="Postcode/ZIP", widget=LongerTextInput)
    country = forms.CharField(required=False,
                              help_text="We'll assume %s if left blank" % settings.PEEPS_DEFAULT_COUNTRY,
                              widget=LongerTextInput)
    phone = forms.CharField(required=True,
                            help_text="We rarely call artists. We need this in case there's a urgent problem.",
                            widget=LongerTextInput)
    email = forms.CharField(required=True, help_text="We contact you at this address. "
                                                     "Also, we create an on-line management account with this address.",
                            widget=LongerTextInput)
    email_confirm = forms.CharField(required=True,
                                    help_text="To ensure correctness, please type your e-mail address again.",
                                    widget=LongerTextInput)

    class Meta:
        model = Person
        exclude = ("reg_id", "comment")

    def clean_email_confirm(self):
        email_confirm = self.cleaned_data['email_confirm']
        try:
            if self.cleaned_data['email'] != email_confirm:
                raise forms.ValidationError("The two e-mails don't match. Please re-enter both carefully.")
        except KeyError:
            pass
        return email_confirm


def main(request):
    if settings.ARTSHOW_SHUT_USER_EDITS:
        return render(request, "artshow/registration_closed.html")


    if request.method == "POST":
        artist_form = ArtistRegisterForm(request.POST)
        person_form = PersonForm(request.POST)
        agreement_form = AgreementForm(request.POST)
        if person_form.is_valid() and artist_form.is_valid():
            email = person_form.cleaned_data['email']
            if User.objects.filter(Q(email=email) or Q(username=email)).exists():
                return render(request, "artshow/manage_register_error.html",
                              {"error": "There is someone else using that email address."})
            try:
                user = create_user_from_email(email)
            except ValueError, x:
                return render(request, "artshow/manage_register_error.html",
                              {"error": str(x)})
            person = person_form.save()
            artist = Artist(person=person, publicname=artist_form.cleaned_data.get('artist_name',''))
            artist.save()
            artist_access = ArtistAccess(artist=artist, user=user, can_edit=True)
            artist_access.save()
            send_password_reset_email(artist, user)
            return render(request, "artshow/manage_register_success.html",
                {"new_user":user, "person":person, "artist":artist})
    else:
        artist_form = ArtistRegisterForm()
        person_form = PersonForm()
        agreement_form = AgreementForm()

    return render(request, "artshow/manage_register_main.html",
                  {"artist_form": artist_form, "person_form": person_form,
                   "agreement_form": agreement_form})










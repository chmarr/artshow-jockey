from django.core.signing import Signer, BadSignature
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from artshow.models import *
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from artshow.utils import artshow_settings
from paypal import make_paypal_url
import utils
import re
import bidsheets
from logging import getLogger

logger = getLogger('paypal')


EXTRA_PIECES = 5


def user_edits_allowable(view_func):
    def decorator(request, *args, **kwargs):
        if artshow_settings.ARTSHOW_SHUT_USER_EDITS:
            error = "The Art Show Administration has disallowed edits for the time being."
            return render(request, "artshow/manage_error.html", {'artshow_settings': artshow_settings,
                                                                 'error': error})
        return view_func(request, *args, **kwargs)
    return decorator


@login_required
def index(request):
    artists = Artist.objects.viewable_by(request.user)
    return render(request, "artshow/manage_index.html", {'artists': artists, 'artshow_settings': artshow_settings})


@login_required
def artist(request, artist_id):

    artist = get_object_or_404(Artist.objects.viewable_by(request.user), pk=artist_id)
    pieces = artist.piece_set.order_by("pieceid")
    payments = artist.payment_set.order_by("date", "id")
    payments_total = payments.aggregate(payments_total=Sum('amount'))['payments_total'] or Decimal(0)
    allocations = artist.allocation_set.order_by("pk")

    can_edit = artist.editable_by(request.user)
    can_edit_personal_details = not artshow_settings.ARTSHOW_SHUT_USER_EDITS and \
                                (request.user.email == artist.person.email)
    can_edit_artist_details = not artshow_settings.ARTSHOW_SHUT_USER_EDITS and can_edit
    can_edit_piece_details = not artshow_settings.ARTSHOW_SHUT_USER_EDITS and can_edit
    can_edit_space_reservations = not artshow_settings.ARTSHOW_SHUT_USER_EDITS and can_edit

    return render(request, "artshow/manage_artist.html",
                  {'artist': artist, 'pieces': pieces, 'allocations': allocations,
                   'payments': payments, 'payments_total': payments_total,
                   'can_edit_personal_details': can_edit_personal_details,
                   'can_edit_artist_details': can_edit_artist_details,
                   'can_edit_piece_details': can_edit_piece_details,
                   'can_edit_space_reservations': can_edit_space_reservations,
                   'artshow_settings': artshow_settings})


class PieceForm(forms.ModelForm):
    class Meta:
        model = Piece
        fields = ('pieceid', 'name', 'media', 'not_for_sale', 'adult', 'min_bid', 'buy_now')
        widgets = {
            'pieceid': forms.TextInput(attrs={'size': 4}),
            'name': forms.TextInput(attrs={'size': 40}),
            'media': forms.TextInput(attrs={'size': 40}),
            'min_bid': forms.TextInput(attrs={'size': 5}),
            'buy_now': forms.TextInput(attrs={'size': 5}),
        }


PieceFormSet = inlineformset_factory(Artist, Piece, form=PieceForm,
                                     extra=EXTRA_PIECES,
                                     can_delete=True,
                                     )


class DeleteConfirmForm(forms.Form):
    confirm_delete = forms.BooleanField(
        required=False,
        help_text="You are about to delete pieces. The information is not recoverable. Please confirm."
    )


@login_required
@user_edits_allowable
def pieces(request, artist_id):
    artist = get_object_or_404(Artist.objects.viewable_by(request.user), pk=artist_id)

    if not artist.editable_by(request.user):
        error = "You do not have permissions to edit pieces for this artist."
        return render(request, "artshow/manage_error.html", {'artshow_settings': artshow_settings,
                                                             'error': error})

    pieces = artist.piece_set.order_by("pieceid")

    if request.method == "POST":
        formset = PieceFormSet(request.POST, queryset=pieces, instance=artist)
        delete_confirm_form = DeleteConfirmForm(request.POST)
        if formset.is_valid() and delete_confirm_form.is_valid():
            if not formset.deleted_forms or delete_confirm_form.cleaned_data['confirm_delete']:
                formset.save()
                messages.info(request, "Changes to piece details have been saved")
                return redirect('.')
    else:
        formset = PieceFormSet(queryset=pieces, instance=artist)
        delete_confirm_form = DeleteConfirmForm()

    return render(request, "artshow/manage_pieces.html",
                  {'artist': artist, 'formset': formset, 'delete_confirm_form': delete_confirm_form,
                   'artshow_settings': artshow_settings})


def yesno(b):
    return "yes" if b else "no"


@login_required
def downloadcsv(request, artist_id):
    artist = get_object_or_404(Artist.objects.viewable_by(request.user), pk=artist_id)

    reduced_artist_name = re.sub('[^A-Za-z0-9]+', '', artist.artistname()).lower()
    filename = "pieces-" + reduced_artist_name + ".csv"

    field_names = ['pieceid', 'code', 'title', 'media', 'min_bid', 'buy_now', 'adult', 'not_for_sale']

    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename=" + filename

    c = utils.UnicodeCSVWriter(response)
    c.writerow(field_names)

    for p in artist.piece_set.all():
        c.writerow((p.pieceid, p.code, p.name, p.media, p.min_bid, p.buy_now, yesno(p.adult), yesno(p.not_for_sale)))

    return response


@login_required
def bid_sheets(request, artist_id):
    artist = get_object_or_404(Artist.objects.viewable_by(request.user), pk=artist_id)

    response = HttpResponse(mimetype="application/pdf")
    bidsheets.generate_bidsheets_for_artists(output=response, artists=[artist])
    return response


@login_required
def control_forms(request, artist_id):
    artist = get_object_or_404(Artist.objects.viewable_by(request.user), pk=artist_id)

    response = HttpResponse(mimetype="application/pdf")
    bidsheets.generate_control_forms(output=response, artists=[artist])
    return response


def allocation_form_factory(available_space_types):
    class AllocationForm(forms.ModelForm):
        space = forms.ModelChoiceField(queryset=available_space_types)

        class Meta:
            model = Allocation
            fields = ('space', 'requested')

        def clean(self):
            cleaned_data = super(AllocationForm, self).clean()
            try:
                if self.instance.space != cleaned_data['space']:
                    raise forms.ValidationError(
                        "You were somehow able to try to change the space type. "
                        "Instead, set one space to zero, and create another.")
            except Space.DoesNotExist:
                pass
            return cleaned_data

    return AllocationForm


@login_required
@user_edits_allowable
def spaces(request, artist_id):
    artist = get_object_or_404(Artist.objects.editable_by(request.user), pk=artist_id)

    allocations = artist.allocation_set.order_by("id")
    available_space_types = Space.objects.filter(reservable=True) | Space.objects.filter(
        pk__in=allocations.values('space'))

    AllocationForm = allocation_form_factory(available_space_types)
    AllocationFormSet = inlineformset_factory(Artist, Allocation, form=AllocationForm, can_delete=False)

    if request.method == "POST":
        formset = AllocationFormSet(request.POST, queryset=allocations, instance=artist)
        if formset.is_valid():
            formset.save()
            messages.info(request, "Changes to your space requests have been saved")
            return redirect(reverse('artshow.manage.artist', args=(artist_id,)))
    else:
        formset = AllocationFormSet(queryset=allocations, instance=artist)

    return render(request, "artshow/manage_spaces.html", {"artist": artist, "formset": formset,
                                                          "artshow_settings": artshow_settings})


class ArtistModelForm(forms.ModelForm):
    publicname = forms.CharField(label="Artist Name", required=False,
                                 help_text="The name we'll display to the public. "
                                           "Make this blank to use your real name")

    class Meta:
        model = Artist
        fields = ('publicname', 'mailin')


@login_required
@user_edits_allowable
def artist_details(request, artist_id):
    artist = get_object_or_404(Artist.objects.editable_by(request.user), pk=artist_id)

    if request.method == "POST":
        form = ArtistModelForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            messages.info(request, "Changes to your artist details have been saved")
            return redirect(reverse('artshow.manage.artist', args=(artist_id,)))
    else:
        form = ArtistModelForm(instance=artist)

    return render(request, "artshow/manage_artist_details.html", {"artist": artist, "form": form,
                                                                  "artshow_settings": artshow_settings})


class PersonModelForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ('name', 'address1', 'address2', 'city', 'state', 'postcode', 'country', 'phone')


@login_required
@user_edits_allowable
def person_details(request, artist_id):
    artist = get_object_or_404(Artist.objects.editable_by(request.user), pk=artist_id)
    person = artist.person
    if person.email != request.user.email:
        error = "You do not have permission to edit this person's details. Please make this request by " \
                "submitting to the Art Show Administration."
        return render(request, "artshow/manage_error.html", {"artshow_settings": artshow_settings, "error": error})

    if request.method == "POST":
        form = PersonModelForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.info(request, "Changes to your personal details have been saved")
            return redirect(reverse('artshow.manage.artist', args=(artist_id,)))
    else:
        form = PersonModelForm(instance=person)

    return render(request, "artshow/manage_person_details.html", {"person": person, "artist": artist,
                                                                  "form": form,
                                                                  "artshow_settings": artshow_settings})


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount",)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be above zero")
        return amount


@login_required
@user_edits_allowable
def make_payment(request, artist_id):
    artist = get_object_or_404(Artist.objects.editable_by(request.user), pk=artist_id)
    allocations = artist.allocation_set.order_by("id")
    total_requested_cost = 0
    for a in allocations:
        total_requested_cost += a.space.price * a.requested
    space_fee = PaymentType(id=settings.ARTSHOW_SPACE_FEE_PK)
    payment_pending = PaymentType(id=settings.ARTSHOW_PAYMENT_PENDING_PK)
    # Deductions from accounts are always negative, so we re-negate it.
    deduction_to_date = - (
        artist.payment_set.filter(payment_type=space_fee).aggregate(amount=Sum("amount"))["amount"] or 0)
    deduction_remaining = total_requested_cost - deduction_to_date
    if deduction_remaining < 0:
        deduction_remaining = 0
    account_balance = artist.payment_set.aggregate(amount=Sum("amount"))["amount"] or 0
    payment_remaining = deduction_remaining - account_balance
    if payment_remaining < 0:
        payment_remaining = 0

    payment = Payment(artist=artist, amount=payment_remaining, payment_type=payment_pending,
                      description="PayPal pending confirmation", date=now())
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            via_mail = request.POST.get("via_mail", "")
            if via_mail:
                payment.description = "Mail-in pending receipt"
            form.save()
            if via_mail:
                return redirect(reverse("artshow.manage.payment_made_email", args=(artist_id,)))
            else:
                url = make_paypal_url(request, payment)
                return redirect(url)
    else:
        form = PaymentForm(instance=payment)

    context = {"form": form,
               "artist": artist,
               "allocations": allocations,
               "total_requested_cost": total_requested_cost,
               "deduction_to_date": deduction_to_date,
               "deduction_remaining": deduction_remaining,
               "account_balance": account_balance,
               "payment_remaining": payment_remaining
               }

    return render(request, "artshow/make_payment.html", context)


@login_required
def payment_made_email(request, artist_id):
    artist = get_object_or_404(Artist.objects.editable_by(request.user), pk=artist_id)
    return render(request, "artshow/payment_made_email.html", {"artist":artist})

@login_required
@csrf_exempt
def payment_made_paypal(request, artist_id):
    artist = get_object_or_404(Artist.objects.editable_by(request.user), pk=artist_id)
    logger.debug ( "paypal post data: %s", request.body )
    return render(request, "artshow/payment_made_paypal.html", {"artist":artist})

@login_required
@csrf_exempt
def payment_cancelled_paypal(request, artist_id):
    artist = get_object_or_404(Artist.objects.editable_by(request.user), pk=artist_id)
    signer = Signer()
    payment_found_and_deleted = False
    try:
        item_number = request.GET["item_number"]
        payment_id = signer.unsign(item_number)
        payment = Payment.objects.get(id=payment_id)
        if payment.artist == artist and payment.payment_type_id == settings.ARTSHOW_PAYMENT_PENDING_PK:
            payment.delete()
            payment_found_and_deleted = True
    except (KeyError, BadSignature, Payment.DoesNotExist):
        pass

    return render(request, "artshow/payment_cancelled_paypal.html",
                  {"artist": artist,
                   "payment_found_and_deleted": payment_found_and_deleted})

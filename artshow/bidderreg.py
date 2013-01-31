from django import forms
from django.contrib.formtools.wizard.views import CookieWizardView
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from artshow.models import Person

class BidderRegistrationForm0 ( forms.Form ):
	pass

class BidderRegistrationForm1 ( forms.Form ):
	name = forms.CharField ( max_length=100, help_text = "Your real, first and last name. This should match your identification." )
	reg_id = forms.CharField ( max_length=20, help_text = "The number on the front of your convention badge. It looks like 123-456, and may have fewer or more digits. Enter the dash, too." )
	cell_contact = forms.CharField ( max_length=40, required=False,
			help_text = "If you have one, provide your cell number or that of a friend." )
	other_contact = forms.CharField ( max_length=100, required=False, 
			help_text = "Optionally, another way to contact you during the convention, such as your hotel and room number." )
	details_changed = forms.BooleanField ( initial=False, required=False,
			help_text = "When you registered at the convention, you provided your address and e-mail. Have these changed since then?" )
	
	def clean ( self ):
		cleaned_data = super(BidderRegistrationForm1, self).clean ()
		cell_contact = cleaned_data.get("cell_contact")
		other_contact = cleaned_data.get("other_contact")
		if cell_contact == "" and other_contact == "":
			raise forms.ValidationError ( "Please enter at least one way to contact you at the show." )
		return cleaned_data
	
class BidderRegistrationForm2 ( forms.Form ):
	address1 = forms.CharField ( max_length = 100, required=False )
	address2 = forms.CharField ( max_length = 100, required=False )
	city = forms.CharField ( max_length = 100, required=False )
	state = forms.CharField ( max_length = 40, required=False )
	postcode = forms.CharField ( max_length = 20, required=False )
	country = forms.CharField ( max_length = 40, required=False )
	email = forms.CharField ( max_length = 100, required=False )
	
def do_print_bidder_registration_form ( person ):
	pass

class BidderRegistrationWizard ( CookieWizardView ):
	template_name = "artshow/bidderreg_wizard.html"
	
	def done ( self, form_list, **kwargs ):
	
		p = None
		for form in form_list:
			cleaned_data = form.cleaned_data
			if isinstance( form, BidderRegistrationForm1 ):
				p = Person (
						name = cleaned_data['name'],
						phone = cleaned_data.get('cell_contact',''),
						reg_id = cleaned_data['reg_id'],
						)
				other_contact = cleaned_data.get('other_contact','')
				if other_contact:
					p.comment = "Other contact: " + other_contact
			elif isinstance ( form, BidderRegistrationForm2 ):
				p.address1 = cleaned_data.get('address1','')
				p.address2 = cleaned_data.get('address2','')
				p.city = cleaned_data.get('city','')
				p.state = cleaned_data.get('state','')
				p.postcode = cleaned_data.get('postcode','')
				p.country = cleaned_data.get('country','')
				p.email = cleaned_data.get('email','')
		p.save()
		do_print_bidder_registration_form ( p )
		return redirect ( final )
		
def final ( request ):
	return render ( request, "artshow/bidderreg_final.html" )
	
def process_step_2 ( wizard ):
	cleaned_data = wizard.get_cleaned_data_for_step('1') or {}
	return cleaned_data.get('details_changed',False)

bidderreg_wizard_view = BidderRegistrationWizard.as_view ( [BidderRegistrationForm0,BidderRegistrationForm1,BidderRegistrationForm2],
		condition_dict={'2':process_step_2} )
		
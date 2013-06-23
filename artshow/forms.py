from django import forms

class ArtistDetailsForm(forms.Form):
    artist_name = forms.CharField(required=False, help_text="Your \"Artist Name\" is what we'll present to the public.")
    use_real_name = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(ArtistRegisterForm, self).clean()
        if bool(cleaned_data['artist_name']) == bool(cleaned_data['use_real_name']):
            raise forms.ValidationError(
                "Please choose either \"Use Real Name\" or a different artist name. Not both. Not neither.")
        return cleaned_data

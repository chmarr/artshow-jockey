from django import forms


class LongerTextInput(forms.TextInput):
    def __init__(self, attrs=None, **kwargs):
        attrs = attrs if attrs is not None else {}
        attrs.setdefault("size","60")
        super(LongerTextInput, self).__init__(attrs, **kwargs)


class ArtistRegisterForm(forms.Form):
    artist_name = forms.CharField(required=False, help_text="Your \"Artist Name\" is what we'll present to the public.",
                                  widget=LongerTextInput)
    use_real_name = forms.BooleanField(required=False,
                                       help_text="If selected, we'll show your real name as your artist name.")

    def clean(self):
        cleaned_data = super(ArtistRegisterForm, self).clean()
        artist_name_entered = bool(cleaned_data['artist_name'])
        use_real_name = bool(cleaned_data['use_real_name'])

        if not artist_name_entered and not use_real_name:
            raise forms.ValidationError(
                "Please enter your preferred artist name, or select \"Use real name\"")
        elif artist_name_entered and use_real_name:
            raise forms.ValidationError(
                "Enter an artist name or \"Use real name\", but not both.")

        return cleaned_data

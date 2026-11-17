from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UploadForm(forms.Form):
    name = forms.CharField(max_length=160, label='Dataset name')
    file = forms.FileField(help_text='CSV with order_date, customer, product, country, quantity, unit_price. Max 2 MB / 10,000 rows.')
    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.csv'):
            raise forms.ValidationError('Only .csv files are supported.')
        if f.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Maximum size is 2 MB.')
        return f

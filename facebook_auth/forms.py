from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.admin.widgets import AdminDateWidget
class ImageUploadForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField(required=False)


class Experience_Campain(forms.Form):
    name = forms.CharField(required=False)
    objective = forms.CharField(required=False)
    niche = forms.CharField(required=False)
    age_max = forms.CharField(required=False)
    age_min = forms.CharField(required=False)
    genders = forms.CharField(required=False)
    created_time = forms.CharField(required=False)
    location_types = forms.CharField(required=False)
    country = forms.CharField(required=False)
    citie = forms.CharField(required=False)
    region = forms.CharField(required=False)
    device_platforms = forms.CharField(required=False)
    publisher_platforms = forms.CharField(required=False)
    positions = forms.CharField(required=False)


class Export_Form(forms.Form):
    model = forms.CharField(required=False)


class Experience_Mode(forms.Form):
    mode = forms.CharField(required=True)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email','password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control','placeholder':'Username','type':'text'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'First Name','type':'text'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Last Name','type':'text'}),
            'email': forms.TextInput(attrs={'class': 'form-control','placeholder':'Email','type':'email'}),
            'password': forms.TextInput(attrs={'class': 'form-control','placeholder':'Password','type':'password'}),
        }

class Edit_Profile(forms.ModelForm):
    mobile_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Mobil Number','type':'text'}), required=False)

    class Meta:
        model = UserProfile
        fields = ['birth_date','location','mobile_number']
        widgets = {             
            # 'birth_date': AdminDateWidget(attrs={'class': 'form-control','placeholder':'Birth Date','type':'text'}), 'placeholder':'Select a date',
            'birth_date': forms.DateInput(format=('%d/%m/%Y'), attrs={'class':'form-control datepicker', 'id':'birth_date','placeholder':'Select a date','type':'text'}),
            'location': forms.TextInput(attrs={'class': 'form-control','placeholder':'Lacation','type':'text'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control','placeholder':'Mobil Number','type':'text'}),
        }

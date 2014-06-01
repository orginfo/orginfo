from django import forms

class OrganizationForm(forms.Form):
    user = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
    name = forms.CharField()

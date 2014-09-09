from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from crispy_forms.bootstrap import StrictButton
from accounting.models import Payment, Client, RealEstate
from django.forms.widgets import TextInput

class OrganizationForm(forms.Form):
    name = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            Fieldset(
                'Organization settings',
                'name',
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn-default')
            )
        )


class ExampleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExampleForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            Fieldset(
                '{{ client }}',
                'amount',
            ),
            ButtonHolder(
                Submit('submit', 'Take', css_class='btn-default')
            )
        )
    class Meta:
        model = Payment
        fields = ['amount']

class LastNameSearchForm(forms.Form):
    name = forms.CharField(max_length=10, required=False)
    def __init__(self, *args, **kwargs):
        super(LastNameSearchForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'name',
            StrictButton('Find', css_class='btn-default', type='submit'),
        )

class AddClientForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddClientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            Fieldset(
                'Add client',
                'lfm',
            ),
            ButtonHolder(
                Submit('submit', 'Add', css_class='btn-default')
            )
        )
    class Meta:
        model = Client
        fields = ['lfm']

class CreateRealEstateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateRealEstateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            Fieldset(
                'Real estate',
                'address',
                'parent',
                'cold_water_counter_setup_date',
                'type',
            ),
            ButtonHolder(
                Submit('submit', 'Take', css_class='btn-default')
            )
        )
    class Meta:
        model = RealEstate
        #fields = ['amount']
        widgets = {
#            'parent': TextInput(),
        }

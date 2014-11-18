from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Field
from crispy_forms.bootstrap import StrictButton
from accounting.models import Payment, Client, RealEstate, ColdWaterReading, ServiceClient
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

class CreateClientForm(ModelForm):
    parent_street = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(CreateClientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            'lfm',
            'real_estate',
            'parent_street',
            ButtonHolder(
                Submit('submit', 'Add', css_class='btn-default')
            )
        )
    class Meta:
        model = Client
        fields = ['lfm', 'real_estate']
    def clean(self):
        #TODO: добавить проверку на пустоту.
        parent_street = self.cleaned_data['parent_street']
        error_messages = []

        # validate piece
        if RealEstate.objects.filter(address__contains=parent_street).count() is not 1:
            error_messages.append('Illegal Piece selected')
            #self._errors["parent_street"] = self.error_class(["Please enter a valid model"])
            pass

        if len(error_messages):
            raise forms.ValidationError(' & '.join(error_messages))

        return self.cleaned_data

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
                Field('cold_water_counter_setup_date', placeholder="ГГГГ-ММ-ДД"),
                'type',
                'residential',
                'residents',
            ),
            ButtonHolder(
                Submit('submit', 'Take', css_class='btn-default')
            )
        )
    class Meta:
        model = RealEstate
        fields = ['address', 'parent', 'cold_water_counter_setup_date', 'type', 'residential', 'residents']
        widgets = {
#            'parent': TextInput(),
        }

class CreateColdWaterReadingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateColdWaterReadingForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['period'].label = "Период"
        self.fields['value'].label = "Показание"
        self.fields['date'].label = "Дата"
        self.helper.layout = Layout(
            Fieldset(
                'Показание счетчика холодного водоснабжения',
                'period',
                'value',
                Field('date', placeholder="ГГГГ-ММ-ДД"),
            ),
            ButtonHolder(
                Submit('submit', 'Create', css_class='btn-default')
            )
        )
    class Meta:
        model = ColdWaterReading
        fields = ['period', 'value', 'date']

class CreateClientServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateClientServiceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            'service_name',
            Field('start', placeholder="ГГГГ-ММ-ДД"),
            Field('end', placeholder="ГГГГ-ММ-ДД"),
            ButtonHolder(
                Submit('submit', 'Create', css_class='btn-default')
            )
        )
    class Meta:
        model = ServiceClient
        fields = ['service_name', 'start', 'end']

class CreateServiceUsageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateServiceUsageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['service_name'].label = "Услуга"
        self.fields['start'].label = "Дата подключения"
        self.fields['end'].label = "Дата отключения"
        self.helper.layout = Layout(
            Fieldset(
                'client service',
                'service_name',
                Field('start', placeholder="ГГГГ-ММ-ДД"),
                Field('end', placeholder="ГГГГ-ММ-ДД"),
            ),
            ButtonHolder(
                Submit('submit', 'Create', css_class='btn-default')
            )
        )
    class Meta:
        model = ServiceClient
        fields = ['service_name', 'start', 'end']

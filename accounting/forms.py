from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Field
from crispy_forms.bootstrap import StrictButton
from accounting.models import Payment, RealEstate, ColdWaterReading, ServiceClient, Account, Organization, LandPlotAndOutbuilding
from django.forms.widgets import TextInput

class OrganizationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['name'].label = "Название"
        self.fields['address'].label = "Адрес"
        self.fields['rs'].label = "р/с"
        self.fields['ks'].label = "к/с"
        self.fields['bik'].label = "БИК"
        self.fields['inn'].label = "ИНН"
        self.fields['phone'].label = "Телефон"
        self.fields['fax'].label = "Факс"
        self.fields['email'].label = "Электронная почта"
        self.fields['operation_mode'].label = "Время работы"
        self.helper.layout = Layout(
            'name',
            'address',
            'rs',
            'ks',
            'bik',
            'inn',
            'phone',
            'fax',
            'email',
            'operation_mode',
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn-default')
            )
        )
    class Meta:
        model = Organization
        fields = ['name', 'address', 'rs', 'ks', 'bik', 'inn', 'phone', 'fax', 'email', 'operation_mode']


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

class AddressSearchForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    def __init__(self, *args, **kwargs):
        super(AddressSearchForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.fields['name'].label = ""
        self.helper.layout = Layout(
            Field('name', placeholder="Адрес"),
            StrictButton('Найти', css_class='btn-default', type='submit'),
        )

class CreateRealEstateForm(ModelForm):
    parent_street = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(CreateRealEstateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['address'].label = "Адрес"
        self.fields['region'].label = "Регион"
        self.fields['parent_street'].label = "Адрес родительской недвижимости"
        self.fields['cold_water_counter_setup_date'].label = "Дата установки счетчика холодного водоснабжения"
        self.fields['type'].label = "Тип"
        self.fields['space'].label = "Площадь"
        self.fields['space_of_joint_estate'].label = "Площадь помещений общего пользования"
        self.fields['residential'].label = "Жилое помещение"
        self.fields['residents'].label = "Количество проживающих"
        self.fields['degree_of_improvements'].label = "Степень благоустройтва жилого помещения"
        self.fields['floor_amount'].label = "Количество этажей"
        self.fields['commissioning_date'].label = "Дата ввода здания в эксплуатацию"
        self.helper.layout = Layout(
            Fieldset(
                'Недвижимость',
                'address',
                'region',
                'parent_street',
                Field('cold_water_counter_setup_date', placeholder="ДД.ММ.ГГГГ"),
                'type',
                'space',
                'space_of_joint_estate',
                'residential',
                'residents',
                'degree_of_improvements',
                'floor_amount',
                'commissioning_date',
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
            )
        )
    class Meta:
        model = RealEstate
        fields = ['address', 'region', 'cold_water_counter_setup_date', 'type', 'space', 'space_of_joint_estate', 'residential', 'residents', 'degree_of_improvements', 'floor_amount', 'commissioning_date']
        widgets = {
#            'parent': TextInput(),
        }
    def clean(self):
        error_messages = []

        # validate piece
        if self.cleaned_data['parent_street'] is not '':
            parent_street = self.cleaned_data['parent_street']
            if RealEstate.objects.filter(address=parent_street).count() is not 1:
                #self._errors["parent_street"] = self.error_class(["Please enter a valid model"])
                error_messages.append('Illegal Piece selected')

        if len(error_messages):
            raise forms.ValidationError(' & '.join(error_messages))

        return self.cleaned_data

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
                Field('date', placeholder="ДД.ММ.ГГГГ"),
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
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
            Field('start', placeholder="ДД.ММ.ГГГГ"),
            Field('end', placeholder="ДД.ММ.ГГГГ"),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
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
                'Услуга',
                'service_name',
                Field('start', placeholder="ДД.ММ.ГГГГ"),
                Field('end', placeholder="ДД.ММ.ГГГГ"),
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
            )
        )
    class Meta:
        model = ServiceClient
        fields = ['service_name', 'start', 'end']

class CreateAccountForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['owners'].label = "Владельцы"
        self.fields['balance'].label = "Баланс"
        self.helper.layout = Layout(
            Fieldset(
                'Лицевой счёт',
                'owners',
                'balance'
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
            )
        )
    class Meta:
        model = Account
        fields = ['balance', 'owners']

class WhatAccountForm(forms.Form):
    name = forms.ChoiceField(choices=(), required=False, widget=forms.Select(attrs={"onChange":'document.getElementsByTagName("form")[0].submit();'}))
    def __init__(self, name_choices, *args, **kwargs):
        super(WhatAccountForm, self).__init__(*args, **kwargs)

        self.fields['name'].choices = name_choices
        self.fields['name'].label = "Лицевой счёт"

        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-6'
        self.helper.layout = Layout(
            'name',
        )

class CreatePaymentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreatePaymentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['amount'].label = "Сумма"
        self.fields['date'].label = "Дата"
        self.fields['comment'].label = "Примечание"
        self.helper.layout = Layout(
            Fieldset(
                'Лицевой счёт',
                'amount',
                Field('date', placeholder="ДД.ММ.ГГГГ"),
                'comment'
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
            )
        )
    class Meta:
        model = Payment
        fields = ['amount', 'date', 'comment']

class CreateLandPlotAndOutbuildingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateLandPlotAndOutbuildingForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['count'].label = "Количество"
        self.fields['direction_using_norm'].label = "Норма направления использования"
        self.helper.layout = Layout(
            Fieldset(
                'Направление использования',
                'count',
                'direction_using_norm'
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
            )
        )
    class Meta:
        model = LandPlotAndOutbuilding
        fields = ['count', 'direction_using_norm']

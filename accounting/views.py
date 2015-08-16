from django.http import HttpResponse
from accounting.models import SubjectRF, Account
from accounting.models import Period, CalculationService, AccountOperation
from accounting.models import RealEstate, HomeownershipHistory, RealEstateOwner
from accounting.models import CommunalService, ClientService, Organization, HouseAddress
from accounting.models import WaterNormDescription
from accounting.models import TechnicalPassport, UserOrganization, CounterReading, Counter
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Sum
from django.views.generic import ListView, CreateView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Field
from django.core.urlresolvers import reverse
from accounting.management.commands.runrobot import get_tariff, get_water_norm
import decimal

import locale
import threading
from contextlib import contextmanager
LOCALE_LOCK = threading.Lock()

@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


def get_residents(real_estate, period):
    """ Возвращает количество проживающих в 'real_estate' за расчетный период 'period'.
    Полагаем, что количество проживающих за один расчетный период постоянно. Если нужно будет учитывать не по расчетному периоду, а по дате, тогда возвращать кортеж: 'количество дней, количество проживающх'"""
    homeownership = HomeownershipHistory.objects.filter(Q(real_estate=real_estate) & Q(water_description__direction_type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING) & Q(start__lte=period.end)).order_by('-start')[0]
    
    # Поле 'count' в таблице HomeownershipHistory имеет тип float. Преобразуем к целому.
    residents = int(homeownership.count)
    return residents

def get_owner(real_estate, period):
    owner = RealEstateOwner.objects.filter(Q(real_estate=real_estate) & Q(start__lte=period.end)).order_by('-start')[0]
    return owner

def get_real_estate_space(real_estate):
    
    technical_pasport = TechnicalPassport.objects.get(real_estate=real_estate)
    return technical_pasport.space if technical_pasport.space is not None else ""

def get_client_services(real_estate, period):
    services = []
    for client_service in ClientService.objects.filter(real_estate=real_estate).order_by('service'):
        services.append(client_service.service)
    return services

def get_payment_amount(real_estate, period):
    amount = 0.0
    for payment_amount in CalculationService.objects.filter(real_estate=real_estate, period=period):
        amount = amount + payment_amount.amount
    
    return amount

@login_required(login_url="/login/")
def index(request):
    return render(request, 'accounting/index.html')

class CounterReadingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CounterReadingForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.fields['counter'].label = "Счётчик"
        self.fields['date'].label = "Дата"
        self.fields['period'].label = "Период"
        self.fields['value'].label = "Показание"
        self.helper.layout = Layout(
            Fieldset(
                'Показание счетчика холодного водоснабжения',
                'counter',
                Field('date', placeholder="ДД.ММ.ГГГГ"),
                'period',
                'value',
            ),
            ButtonHolder(
                Submit('submit', 'Сохранить', css_class='btn-default')
            )
        )
    class Meta:
        model = CounterReading
        fields = ['counter', 'date', 'period', 'value']

class CounterReadingTab(CreateView):
    model = CounterReading
    form_class = CounterReadingForm
    template_name = 'accounting/counter_reading_tab.html'
    def get_form(self, form_class):
        form = super(CounterReadingTab,self).get_form(form_class)
        form.fields['counter'].queryset = Counter.objects.filter(real_estate__id=self.real_estate_id)
        return form
    def get_success_url(self):
        return reverse('accounting:create_reading')
    def form_valid(self, form):
        form.instance.real_estate_id = self.real_estate_id
        return super(CounterReadingTab, self).form_valid(form)
    def dispatch(self, *args, **kwargs):
        self.real_estate_id = None
        if 'real_estate' in self.request.GET:
            self.real_estate_id = self.request.GET['real_estate']
        return super(CounterReadingTab, self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(CounterReadingTab, self).get_context_data(**kwargs)

        if self.real_estate_id == None:
            return context

        context['readings'] = CounterReading.objects.filter(counter__real_estate__id=self.real_estate_id)

        real_estate_str = RealEstate.objects.get(id=self.real_estate_id).__str__()
        context['real_estate'] = {
            "id": self.real_estate_id,
            "real_estate_str": real_estate_str
        }
        return context

@login_required(login_url="/login/")
def readings(request):
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    if not user_org.organization:
        raise Http404

    real_estate = None
    context = {}
    ru_people_count = "140000000"
    if ('real_estate' in request.GET and
            len(request.GET["real_estate"]) <= len(ru_people_count) and
            request.GET["real_estate"].isnumeric()):
        real_estates = user_org.organization.abonents.filter(id=request.GET["real_estate"])
        if len(real_estates) == 1:
            real_estate = real_estates[0]
            context["real_estate"] = {
                "id": real_estate.id,
                "real_estate_str": real_estate.__str__()}

    
    return render(request, 'accounting/readings.html', context)

@login_required(login_url="/login/")
def report(request):
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    if not user_org.organization:
        raise Http404
    ru_people_count = "140000000"
    if ('real_estate' not in request.GET or
            len(request.GET["real_estate"]) > len(ru_people_count) or
            request.GET["real_estate"].isnumeric() == False):
        raise Http404
    real_estates = user_org.organization.abonents.filter(id=request.GET["real_estate"])
    if len(real_estates) != 1:
        raise Http404
    real_estate_id = request.GET["real_estate"]
    real_estate = real_estates[0]
    if ('period' not in request.GET or
            len(request.GET["period"]) > 4 or
            request.GET["period"].isnumeric() == False):
        raise Http404
    period_id = request.GET["period"]
    period = Period.objects.get(id=period_id)
    subject_rf = SubjectRF.objects.get(name="Новосибирская область")

    context = {}

    #with setlocale('ru_RU.UTF-8'):
    context["calc_period_name"] = period.end.strftime("%B %Y")
    context["owner"] = get_owner(real_estate, period)
    context["client_address"] = RealEstate.get_full_address(real_estate)
    context["space"] = get_real_estate_space(real_estate)
    context["residents"] = get_residents(real_estate, period)
    organization = user_org.organization
    context["organization_name"] = str(organization)
    context["organization_address"] = HouseAddress.get_full_address(organization.address)
    context["phone"] = "/".join(list(map(lambda x: x.strip(), organization.phone.split(","))))
    context["fax"] = organization.fax
    context["email"] = organization.email
    context["website"] = organization.website
    context["operating_mode"] = organization.operating_mode

    context["resourse_supply_organizations"] = []
    for resourse_supply_organization in Organization.objects.filter(abonents=real_estate):
        context["resourse_supply_organizations"].append({
            "organization_name": str(resourse_supply_organization),
            "bank_identifier_code": resourse_supply_organization.bank_identifier_code,
            "corresponding_account": resourse_supply_organization.corresponding_account,
            "operating_account": resourse_supply_organization.operating_account,
            "account_number": Account.objects.get(real_estate=real_estate).__str__(),
            "services": get_client_services(real_estate, period)
        })

    context["account_info"] = {}
    # Задолженность за предыдующие периоды
    operation = AccountOperation.objects.get(real_estate=real_estate, operation_type=AccountOperation.WRITE_OFF, operation_date=period.start)
    debts = decimal.Decimal(operation.balance) if operation.balance < 0.0 else decimal.Decimal(0.0)
    context["account_info"]["debts"] = debts
    # Аванс на начало расчетного периода
    operation = AccountOperation.objects.filter(real_estate=real_estate, operation_date__lte=period.end).order_by('operation_date').last()
    advance = decimal.Decimal(0.0) if operation.balance < 0.0 else operation.balance
    context["account_info"]["advance"] = advance
    # Дата последней оплаты:
    context["account_info"]["last_payment_date"] = "--"
    operation = AccountOperation.objects.filter(real_estate=real_estate, operation_type=AccountOperation.TOP_UP, operation_date__lte=period.end).order_by('operation_date').last()
    if operation is not None: 
        context["account_info"]["last_payment_date"] = operation.operation_date
    # Оплата за все услуги для расчетного периода
    payment_amount = CalculationService.objects.filter(real_estate=real_estate, period=period).aggregate(Sum('amount'))['amount__sum'] or 0.0
    payment_amount = decimal.Decimal(payment_amount)
    # Итого к оплате:
    context["account_info"]["total_amount"] = -(advance + debts - payment_amount)

    return render(request, 'accounting/empty_report.html', context)

@login_required(login_url="/login/")
def reportTODO(request):
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    if not user_org.organization:
        raise Http404
    ru_people_count = "140000000"
    if ('real_estate' not in request.GET or
            len(request.GET["real_estate"]) > len(ru_people_count) or
            request.GET["real_estate"].isnumeric() == False):
        raise Http404
    real_estates = user_org.organization.abonents.filter(id=request.GET["real_estate"])
    if len(real_estates) != 1:
        raise Http404
    real_estate_id = request.GET["real_estate"]
    real_estate = real_estates[0]
    if ('period' not in request.GET or
            len(request.GET["period"]) > 4 or
            request.GET["period"].isnumeric() == False):
        raise Http404
    period_id = request.GET["period"]
    period = Period.objects.get(id=period_id)
    subject_rf = SubjectRF.objects.get(name="Новосибирская область")

    context = {}

    with setlocale('ru_RU.UTF-8'):
        context["calc_period_name"] = period.end.strftime("%B %Y")
    context["owner"] = get_owner(real_estate, period)
    context["client_address"] = RealEstate.get_full_address(real_estate)
    context["space"] = get_real_estate_space(real_estate)
    context["residents"] = get_residents(real_estate, period)
    organization = user_org.organization
    context["organization_name"] = str(organization)
    context["organization_address"] = HouseAddress.get_full_address(organization.address)
    context["phone"] = "/".join(list(map(lambda x: x.strip(), organization.phone.split(","))))
    context["fax"] = organization.fax
    context["email"] = organization.email
    context["website"] = organization.website
    context["operating_mode"] = organization.operating_mode

    context["resourse_supply_organizations"] = []
    for resourse_supply_organization in Organization.objects.filter(abonents=real_estate):
        context["resourse_supply_organizations"].append({
            "organization_name": str(resourse_supply_organization),
            "bank_identifier_code": resourse_supply_organization.bank_identifier_code,
            "corresponding_account": resourse_supply_organization.corresponding_account,
            "operating_account": resourse_supply_organization.operating_account,
            "services": get_client_services(real_estate, period),
            "amount": get_payment_amount(real_estate, period)
        })

    context["account_info"] = {}
    # Задолженность за предыдующие периоды
    operation = AccountOperation.objects.get(real_estate=real_estate, operation_type=AccountOperation.WRITE_OFF, operation_date=period.start)
    debts = operation.balance if operation.balance < 0.0 else 0.0
    context["account_info"]["debts"] = debts
    # Аванс на начало расчетного периода
    operation = AccountOperation.objects.filter(real_estate=real_estate, operation_date__lte=period.end).order_by('operation_date').last()
    advance = 0.0 if operation.balance < 0.0 else operation.balance
    context["account_info"]["advance"] = advance
    # Дата последней оплаты:
    context["account_info"]["last_payment_date"] = "--"
    operation = AccountOperation.objects.filter(real_estate=real_estate, operation_type=AccountOperation.TOP_UP, operation_date__lte=period.end).order_by('operation_date').last()
    if operation is not None: 
        context["account_info"]["last_payment_date"] = operation.operation_date
    # Оплата за все услуги для расчетного периода
    payment_amount = CalculationService.objects.filter(real_estate=real_estate, period=period).aggregate(Sum('amount'))['amount__sum'] or 0.0
    # Итого к оплате:
    context["account_info"]["total_amount"] = advance + debts - payment_amount

    context["all_total_amount"] = 0
    context["services"] = [];
    for service in get_client_services(real_estate, period):
        calc_individual_service = CalculationService.objects.get(consumption_type=CalculationService.INDIVIDUAL, period__id=period_id, communal_service=service, real_estate__id=real_estate_id)
        individual_volume = calc_individual_service.volume
        individual_amount = calc_individual_service.amount

        common_property_value = "--"
        common_property_amount = "--"
        total_amount = individual_amount
        calc_common_service = CalculationService.objects.filter(consumption_type=CalculationService.COMMON_PROPERTY, period__id=period_id, communal_service=service, real_estate__id=real_estate_id)
        if len(calc_common_service) == 1:
            common_property_value = calc_common_service.volume
            common_property_amount = calc_common_service.amount
            total_amount = individual_amount + common_property_amount

        context["all_total_amount"] = context["all_total_amount"] + total_amount

        real_estate = RealEstate.objects.get(id=real_estate_id)
        period = Period.objects.get(id=period_id)
        tariff = get_tariff(real_estate, period, service)

        norm = 0.0
        service_name = service.name
        if service_name == CommunalService.HEATING:
            pass
        else:
            homeownership = HomeownershipHistory.objects.filter(real_estate=real_estate, water_description__direction_type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING, start__lte=period.end).order_by('-start')[0]
            water_description = homeownership.water_description
            norm = get_water_norm(subject_rf, water_description, period, service)
        
        context["services"].append({
            "name": service.get_name_display(),
            "individual_volume": individual_volume,
            "common_property_value": common_property_value,
            "tariff": tariff,
            "individual_amount": individual_amount,
            "common_property_amount": common_property_amount,
            "total_amount": total_amount,
            "norm" : norm,
        })

    return render(request, 'accounting/report.html', context)

class Accounts(ListView):
    context_object_name = 'accounts'
    template_name = 'accounting/search_real_estates.html'
    def get_queryset(self):
        if self.real_estate_id == None:
            return []

        periods = Period.objects.all()

        periods_by_id = {}
        for period in periods:
            periods_by_id[period.id] = period

        operations_by_period = {}
        for operation in AccountOperation.objects.filter(real_estate__id=self.real_estate_id):
            for period in periods:
                if period.start <= operation.operation_date and operation.operation_date <= period.end:
                    if period.id not in operations_by_period:
                        operations_by_period[period.id] = []
                    operations_by_period[period.id].append(operation)

        sorted_period_ids = sorted(operations_by_period)
        result = []
        for id in sorted_period_ids:
            result.append({
                "period": periods_by_id[id],
                "balance": operations_by_period[id][-1].balance,
                "operations": operations_by_period[id]
            })
        return result#object_list
    def dispatch(self, *args, **kwargs):
        self.real_estate_id = None
        if 'real_estate' in self.request.GET:
            self.real_estate_id = self.request.GET['real_estate']

        return super(Accounts, self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(Accounts, self).get_context_data(**kwargs)

        if self.real_estate_id == None:
            return context

        real_estate_str = RealEstate.objects.get(id=self.real_estate_id).__str__()
        context['real_estate'] = {
            "id": self.real_estate_id,
            "real_estate_str": real_estate_str
        }
        return context

@login_required(login_url="/login/")
def real_estates_as_options(request):
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    #TODO: уточнить как связаны комнаты и квартира, что бы вывести комнаты без квартиры.
    real_estates = user_org.organization.abonents.filter(Q(type=RealEstate.HOUSE) | Q(type=RealEstate.FLAT))
    words = request.GET['q'].split(" ")
    for word in words:
        real_estates = list(filter(lambda re: word in re.__str__(), real_estates))

    items = list(map(lambda re: {"text": re.__str__(), "id": re.id}, real_estates))

    response_data = {
        "total_count": len(items),
        "incomplete_results": False,
        "items": items
    }
     
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )

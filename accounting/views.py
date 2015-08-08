from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality
from accounting.models import Period, CalculationService, Account
from accounting.models import RealEstate, HomeownershipHistory, RealEstateOwner
from accounting.models import CommunalService, ClientService, Organization
from accounting.models import WaterNormDescription, WaterNormValidity, WaterNorm, TariffValidity, Tariff
from accounting.models import TechnicalPassport, UserOrganization
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from datetime import timedelta
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

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
        except:
            pass
        finally:
            locale.setlocale(locale.LC_ALL, saved)


def get_water_norm(subject_rf, water_description, period, water_service):
    # Получение периода действия норматива по расчетному периоду. Расчетный период устанавливается равным календарному месяцу. Поэтому, считаем, что за один месяц может быть только один норматив.
    validity = WaterNormValidity.objects.filter(start__lte=period.end).order_by('-start')[0]
    
    water_norm = WaterNorm.objects.get(subject_rf=subject_rf, norm_description=water_description, validity=validity, service=water_service)
    return water_norm.value

def get_residents(real_estate, period):
    """ Возвращает количество проживающих в 'real_estate' за расчетный период 'period'.
    Полагаем, что количество проживающих за один расчетный период постоянно. Если нужно будет учитывать не по расчетному периоду, а по дате, тогда возвращать кортеж: 'количество дней, количество проживающх'"""
    homeownership = HomeownershipHistory.objects.filter(Q(real_estate=real_estate) & Q(water_description__direction_type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING) & Q(start__lte=period.end)).order_by('-start')[0]
    
    # Поле 'count' в таблице HomeownershipHistory имеет тип float. Преобразуем к целому.
    residents = int(homeownership.count)
    return residents

def get_tariff(real_estate, period, service):
    # Получение периода действия по расчетному периоду. Расчетный период устанавливается равным календарному месяцу. Поэтому, считаем, что за один месяц может быть только один тариф
    validity = TariffValidity.objects.filter(start__lte=period.end).order_by('-start')[0]
    
    resource_supply_organization = Organization.objects.get(services=service, abonents=real_estate)
    
    tariff_type = None
    if real_estate.type == RealEstate.MUNICIPAL_OBJECT:
        tariff_type = Tariff.BUDGETARY_CONSUMERS
    else:
        tariff_type = Tariff.POPULATION
    
    tafiff = Tariff.objects.get(service=service, organization=resource_supply_organization, validity=validity, type=tariff_type)
    return tafiff.value

def write_off(real_estate, service, period):
    #TODO: Реализовать этот метод и везде его использовать
    pass

def calculate_individual_water_volume_by_norm(subject_rf, real_estate, period, water_service):
    """
    Функция расчета объема услуге по воде по нормативу потребления.
    Используется формула #4.
    """
    if real_estate.type == RealEstate.MUNICIPAL_OBJECT:
        raise Exception #TODO: Продумать ошибку (Для данного типа помещения нельзя расчитать объем. Расчет должен выполняться для внутренних помещений).
    
    # Метода используется только для жилых помещений. Дополнительная проверка на условия не проводится, т.к. здесь может присутствовать либо отстутствовать счетчик (эти условия должны выполняться в методах более высокого уровня)
    if real_estate.residential == False:
        raise Exception #TODO: Продумать ошибку (Вычисление норматива потребления должны вызываться только для жилых помещений).
    
    if HomeownershipHistory.objects.filter(real_estate=real_estate, water_description__direction_type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING, start__lte=period.end).count() != 1:
        encoding = 'utf-8'
        err_file = open('c:\\vitaly\\Reading\\Protocol_SrvNoActive_KK.txt', 'a', encoding=encoding)
        err_desc = str(real_estate) + '\t' + str(period) + '\n'
        err_file.write(err_desc)
        err_file.close()
        return -1
    homeownership = HomeownershipHistory.objects.filter(real_estate=real_estate, water_description__direction_type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING, start__lte=period.end).order_by('-start')[0]
    water_description = homeownership.water_description
    # Получаем количество проживающих.
    #residents = get_residents(real_estate, period)
    residents = int(homeownership.count)
    
    # Получаем норматив потребления
    norm = get_water_norm(subject_rf, water_description, period, water_service)
    
    volume = norm * residents
    return volume

def calculate_individual_water_volume(subject_rf, real_estate, calc_period, water_service):
    individual_volume = calculate_individual_water_volume_by_norm(subject_rf, real_estate, calc_period, water_service)
    
    tariff = get_tariff(real_estate, calc_period, water_service)
    amount = individual_volume * tariff
    
    if amount > 0:
        calc_service = CalculationService(real_estate=real_estate, communal_service=water_service, consumption_type=CalculationService.INDIVIDUAL, period=calc_period, volume=individual_volume, amount=amount)
        calc_service.save()
        
        #TODO: Использовать метод write_off()
        #TODO: Получаем баланс на начало расчетного периода или нужно использовать последний баланс?
        account = Account.objects.filter(real_estate=real_estate).order_by('operation_date').last()
        balance = account.balance - amount
        operation_date = calc_period.end + timedelta(days=1)
        account = Account(real_estate=real_estate, balance=balance, operation_type=Account.WRITE_OFF, operation_date=operation_date, amount=amount)
        account.save()

def calculate_services(subject_rf, house, calc_period):
    real_estates = []
    if house.type == RealEstate.MULTIPLE_DWELLING:
        for real_estate in RealEstate.objects.filter(parent=house):
            real_estates.append(real_estate)
    elif house.type == RealEstate.HOUSE:
        real_estates.append(house) 
    
    # Сперва выполняется расчет индивидуального потребления. Затем, если требуется, расчет ОДН.
    for real_estate in real_estates:
        for client_service in ClientService.objects.filter(real_estate=real_estate).order_by('service'):
            #TODO: Добавить проверку- активна ли услуга в расчетчном периоде.
            service_name = client_service.service.name
            if service_name == CommunalService.COLD_WATER:
                calculate_individual_water_volume(subject_rf, real_estate, calc_period, client_service.service)
            elif service_name == CommunalService.HOT_WATER:
                pass
            elif service_name == CommunalService.HEATING:
                pass
            else:
                pass

    #TODO: Добавить расчет ОДН.
    pass

def robot():
    for subject_rf in SubjectRF.objects.all():
        for municipal_area in MunicipalArea.objects.filter(subject_rf=subject_rf):
            for municipal_union in MunicipalUnion.objects.filter(municipal_area=municipal_area):
                for locality in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union):
                    for period in Period.objects.all().order_by('serial_number'):
                        for real_estate in RealEstate.objects.filter(address__street__locality=locality):
                            calculate_services(subject_rf, real_estate, period)

    pass
                
""" Информация для платежного документа"""
"""Раздел 1. Сведения о плательщике и исполнителе услуг"""
# за ________ расчетный период: Используется табилца Period
# Ф.И.О. (наименование) плательщика собственника/нанимателя: Таблица RealEstateOwner. Для получения вызвать метод get_owner(real_estate, period)
def get_owner(real_estate, period):
    owner = RealEstateOwner.objects.filter(Q(real_estate=real_estate) & Q(start__lte=period.end)).order_by('-start')[0]
    return owner

# Адрес помещения: Таблица RealEstate.
# Площадь помещения. Таблица TechnicalPassport
def get_real_estate_space(real_estate):
    technical_pasport = TechnicalPassport.objects.get(real_estate=real_estate)
    return technical_pasport.space
# Количество проживающих. Хранятся в HomeownershipHistory. Вызвать get_residents(real_estate, period) 
# Наименование организации или Ф.И.О индивидуально предпринимателя - исполнителя услуг: Organization.__str__
# Адрес: Organization.address
# Телефон (Organization.phone), факс (Organization.fax), адрес электронной почты (Organization.email), адрес сайта в сети Интернет:
# Режим работы ___________ (Organization.operating_mode); телефон (Organization.phone)

def test_part1(organization, real_estate, period):
    # за ________ расчетный период:
    calc_period_name = str(period)
    # Ф.И.О. (наименование) плательщика собственника/нанимателя: Таблица RealEstateOwner. Для получения вызвать метод get_owner(real_estate, period)
    owner = get_owner(real_estate, period)
    # Адрес помещения: Таблица RealEstate.
    client_address = str(real_estate)
    # Площадь помещения. Таблица TechnicalPassport
    space = get_real_estate_space(real_estate)
    # Количество проживающих. Хранятся в HomeownershipHistory. Вызвать get_residents(real_estate, period)
    residents = get_residents(real_estate, period)
    # Наименование организации или Ф.И.О индивидуально предпринимателя - исполнителя услуг:
    organization_name = str(Organization)
    # Адрес: Organization.address
    organization_address = str(Organization.address)
    # Телефон организации
    phone = Organization.phone
    # Факс организации
    fax = Organization.fax
    # адрес электронной почты
    email = Organization.email
    # адрес сайта
    website = Organization.website
    # Режим работы ___________
    operating_mode = Organization.operating_mode
    # (operating_mode); телефон 
    phone = Organization.phone

"""Раздел 2. Информация для внесения платы получателю платежа (получателям платежей)"""
# Наименование получателя платежа: Organization.__str__
# Номер банковского счета и банковские реквизиты:
    # Organization.bank_identifier_code # БИК
    # Organization.corresponding_account # Корреспондентский счет
    # Organization.operating_account # Расчетный счет
# Номер лицевого счета: пока не добавлено
# Виды услуг: Таблица ClientService. Вызвать get_client_services(real_estate, period)
def get_client_services(real_estate, period):
    services = []
    for client_service in ClientService.objects.filter(real_estate=real_estate).order_by('service'):
        services.append(client_service.service)
    return services
# Сумма к оплате за расчетный период: Значения хранятся в PaymentAmount. Вызвать метод get_payment_amount(real_estate, period)
def get_payment_amount(real_estate, period):
    amount = 0.0
    for payment_amount in CalculationService.objects.filter(real_estate=real_estate, period=period):
        amount = amount + payment_amount.amount
    
    return amount

# Справочно: Задолженность за предыдущие периоды: пока не добавил
# Аванс на начало расчетного периода (учтены платежи, поступившие до 25 числа расчетного периода включительно) : пока не добавил
# Дата последней поступившей оплаты : пока не добавил
# Итого к оплате : пока не добавил
def test_part2(real_estate, period):
    for resourse_supply_organization in Organization.objects.filter(abonents=real_estate):
        # Наименование получателя платежа:
        organization_name = str(resourse_supply_organization)
        # Номер банковского счета
        bank_identifier_code = Organization.bank_identifier_code
        # Корреспондентский счет
        corresponding_account = Organization.corresponding_account
        # Расчетный счет
        operating_account = Organization.operating_account
        # Виды услуг: Таблица ClientService. Вызвать get_client_services(real_estate, period)
        services = get_client_services(real_estate, period)
        # Сумма к оплате за расчетный период: Значения хранятся в PaymentAmount. Вызвать метод get_payment_amount(real_estate, period)
        amount = get_payment_amount(real_estate, period)

"""Раздел 3. РАСЧЕТ РАЗМЕРА ПЛАТЫ ЗА СОДЕРЖАНИЕ И РЕМОНТ ЖИЛОГО ПОМЕЩЕНИЯ И КОММУНАЛЬНЫЕ УСЛУГИ """


def test_payment_doc():
    for subject_rf in SubjectRF.objects.all():
        for municipal_area in MunicipalArea.objects.filter(subject_rf=subject_rf):
            for municipal_union in MunicipalUnion.objects.filter(municipal_area=municipal_area):
                for locality in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union):
                    for period in Period.objects.all().order_by('serial_number'):
                        for real_estate in RealEstate.objects.filter(address__street__locality=locality):
                            calculate_services(subject_rf, real_estate, period)

def test_period():
    for period in Period.objects.all().order_by('serial_number'):
        pass
def test_owner():
    for subject_rf in SubjectRF.objects.all():
        for municipal_area in MunicipalArea.objects.filter(subject_rf=subject_rf):
            for municipal_union in MunicipalUnion.objects.filter(municipal_area=municipal_area):
                for locality in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union):
                    for period in Period.objects.all().order_by('serial_number'):
                        for real_estate in RealEstate.objects.filter(address__street__locality=locality):
                            owner = get_owner(real_estate, period)

@login_required(login_url="/login/")
def index(request):
    #test_db()
    #test_heating_norm()
    #test_water_tariff()
    #test_service()
    #test_house_address()
    #test_org()
    #test_org_srv()
    #test_real_estate()
    #test_residents_degree()
    
    robot()
    #test_period()
    #test_owner()
    
    return HttpResponse("Робот отработал успешно.")

@login_required(login_url="/login/")
def report(request):
    real_estate_id = 8 #TODO: Параметр.
    real_estate = RealEstate.objects.get(id=real_estate_id)

    period_id = 8 #TODO: Параметр.
    period = Period.objects.get(id=period_id)

    context = {}

    #with setlocale('ru_RU.UTF-8'):
    context["calc_period_name"] = period.end.strftime("%B %Y")
    context["owner"] = get_owner(real_estate, period)
    context["client_address"] = str(real_estate)
    context["space"] = get_real_estate_space(real_estate)
    context["residents"] = get_residents(real_estate, period)
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    organization = user_org.organization
    context["organization_name"] = str(organization)
    context["organization_address"] = str(organization.address)
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

        context["services"] = []
        for client_service in ClientService.objects.filter(real_estate_id=real_estate_id):
            context["services"].append(client_service) 

# Таблица связи, если правильно помню - ClientService
#    "Виды услуг" - ClientService
#    "Единица измерения" - в модели нигде не учитывал единицы измерения. В случае, если используется отопление - "Гкал", в случае водоснабжения и водоотведения - "куб. м"
#    "Объем коммунальных услуг *":
#    - "индивидуальное потребление" - таблица 'CalculationService', для выборки использовать 'CalculationService.consumption_type == CalculationService.INDIVIDUAL'. Объем хранит поле 'CalculationService.volume'
#    - "общедомовые нужды" - тоже, что и "индивидуальное потребление", только для выборки использовать тип 'CalculationService.consumption_type == CalculationService.COMMON_PROPERTY' (на данный момент наши клиенты не используют ОДН).
#    - "Тариф руб./единица измерения" - использовать метод 'def get_tariff(real_estate, period, service):'. Единицы измерения нигде не учитывал. В случае, если используется отопление - "руб./Гкал", в случае водоснабжения и водоотведения - "руб./м3"
#    "Размер платы за коммунальные услуги, руб."
#    - "индивидуальное потребление" - таблица 'CalculationService', для выборки использовать 'CalculationService.consumption_type == CalculationService.INDIVIDUAL'. Объем хранит поле 'CalculationService.amount'
#    - "общедомовые нужды" - тоже, что и "индивидуальное потребление", только для выборки использовать тип 'CalculationService.consumption_type == CalculationService.COMMON_PROPERTY' (на данный момент наши клиенты не используют ОДН).
#    "Всего начислено за расчетный период, руб." - сумма 'CalculationService.amount' за индивидуальное и ОДН.
#    "Перерасчеты всего, руб." - пока не использовать
#    "Льготы, субсидии, руб." - пока не использовать
# последние 3 столбца чуть попозже скажу


#    if not user_org.organization:
#        raise Http404

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

        accounts_by_period = {}
        for account in Account.objects.filter(real_estate__id=self.real_estate_id):
            for period in periods:
                if period.start <= account.operation_date and account.operation_date <= period.end:
                    if period.id not in accounts_by_period:
                        accounts_by_period[period.id] = []
                    accounts_by_period[period.id].append(account)

        sorted_period_ids = sorted(accounts_by_period)
        result = []
        for id in sorted_period_ids:
            result.append({
                "period": periods_by_id[id],
                "balance": accounts_by_period[id][-1].balance,
                "operations": accounts_by_period[id]
            })
        return result#object_list
    def dispatch(self, *args, **kwargs):
        self.real_estate_id = None
        if 'XXX' in self.request.GET:
            self.real_estate_id = self.request.GET['XXX']

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

from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality
from accounting.models import Period, Volume, ConsumptionType, PaymentAmount
from accounting.models import RealEstate, HomeownershipHistory
from accounting.models import CommunalService, ClientService, Organization
from accounting.models import WaterNormDescription, WaterNormValidity, WaterNorm, TariffType, Tariff
from django.db.models import Q
from django.shortcuts import render



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
    validity = WaterNormValidity.objects.filter(start__lte=period.end).order_by('-start')[0]
    
    resource_supply_organization = Organization.objects.get(services_set=service, abonents_set=real_estate)
    
    tariff_type = None
    if real_estate.type == RealEstate.MUNICIPAL_OBJECT:
        tariff_type = TariffType.objects.get(type=TariffType.BUDGETARY_CONSUMERS)
    else:
        tariff_type = TariffType.objects.get(type=TariffType.POPULATION)
    
    tafiff = Tariff.objects.get(service=service, organization=resource_supply_organization, validity=validity, type=tariff_type)

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
    
    homeownership = HomeownershipHistory.objects.filter(Q(real_estate=real_estate) & Q(water_description__direction_type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING) & Q(start__lte=period.end)).order_by('-start')[0]
    water_description = homeownership.water_description
    # Получаем количество проживающих.
    #residents = get_residents(real_estate, period)
    residents = int(homeownership.count)
    
    # Получаем норматив потребления
    norm = get_water_norm(subject_rf, water_description, period, water_service)
    
    volume = norm * residents
    return volume

def calculate_individual_water_volume(subject_rf, real_estate, calc_period, water_service):
    consumption_type = ConsumptionType.objects.get(type=ConsumptionType.INDIVIDUAL)
    individual_volume = calculate_individual_water_volume_by_norm(subject_rf, real_estate, calc_period, water_service)
    volume = Volume(real_estate=real_estate, communal_service=water_service, consumption_type=consumption_type, period=calc_period, volume=individual_volume)
    volume.save()
    
    tariff = get_tariff(real_estate, calc_period, water_service)
    amount = individual_volume * tariff
    payment_amount = PaymentAmount(real_estate=real_estate, communal_service=water_service, consumption_type=consumption_type, period=calc_period, amount=amount)
    payment_amount.save()

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
    
    return HttpResponse("Робот отработал успешно.")

def report(request):
    "the last payment in the organization"
#    user_org = get_object_or_404(UserOrganization, user=request.user.id)
#    if not user_org.organization:
#        raise Http404
#    last_payment = Payment.objects.filter(client__organization=user_org.organization).last()
    context = {
        #'last_payment': last_payment,
        'last_payment': None,
        'period': '2014-06-01 (TODO)'
    }
    return render(request, 'accounting/report.html', context)

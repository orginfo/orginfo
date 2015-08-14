from django.core.management.base import BaseCommand
from datetime import timedelta
from accounting.models import WaterNormValidity, WaterNorm, TariffValidity, Organization, RealEstate, Tariff, HomeownershipHistory, CalculationService, AccountOperation, ClientService, CommunalService, SubjectRF, MunicipalArea, MunicipalUnion, Period, WaterNormDescription, Locality


# def test_payment_doc():
#     for subject_rf in SubjectRF.objects.all():
#         for municipal_area in MunicipalArea.objects.filter(subject_rf=subject_rf):
#             for municipal_union in MunicipalUnion.objects.filter(municipal_area=municipal_area):
#                 for locality in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union):
#                     for period in Period.objects.all().order_by('serial_number'):
#                         for real_estate in RealEstate.objects.filter(address__street__locality=locality):
#                             calculate_services(subject_rf, real_estate, period)
# 
# def test_period():
#     for period in Period.objects.all().order_by('serial_number'):
#         pass
# 
# def test_owner():
#     for subject_rf in SubjectRF.objects.all():
#         for municipal_area in MunicipalArea.objects.filter(subject_rf=subject_rf):
#             for municipal_union in MunicipalUnion.objects.filter(municipal_area=municipal_area):
#                 for locality in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union):
#                     for period in Period.objects.all().order_by('serial_number'):
#                         for real_estate in RealEstate.objects.filter(address__street__locality=locality):
#                             owner = get_owner(real_estate, period)
# 
# def write_off(real_estate, service, period):
#     #TODO: Реализовать этот метод и везде его использовать
#     pass

def get_water_norm(subject_rf, water_description, period, water_service):
    # Получение периода действия норматива по расчетному периоду. Расчетный период устанавливается равным календарному месяцу. Поэтому, считаем, что за один месяц может быть только один норматив.
    validity = WaterNormValidity.objects.filter(start__lte=period.end).order_by('-start')[0]
    
    water_norm = WaterNorm.objects.get(subject_rf=subject_rf, norm_description=water_description, validity=validity, service=water_service)
    return water_norm.value

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
        operation = AccountOperation.objects.filter(real_estate=real_estate).order_by('operation_date').last()
        balance = operation.balance - amount
        operation_date = calc_period.end + timedelta(days=1)
        operation = AccountOperation(real_estate=real_estate, balance=balance, operation_type=AccountOperation.WRITE_OFF, operation_date=operation_date, amount=amount)
        operation.save()

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
                    period = Period.objects.all().last()
                    for real_estate in RealEstate.objects.filter(address__street__locality=locality):
                        calculate_services(subject_rf, real_estate, period)

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'
    def handle(self, *args, **options):
        robot()
        self.stdout.write('The data has been just prepared by robot successfully.')

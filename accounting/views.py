from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality
from accounting.models import Period
from accounting.models import Street, HouseAddress
from accounting.models import Organization
from accounting.models import RealEstate, HomeownershipHistory
from accounting.models import Service, ClientService, OrganizationService
from accounting.models import WaterType, WaterNormDescription, WaterNormValidity, WaterNorm
from accounting.models import HeatingNormValidity, HeatingNorm
from accounting.models import WaterTariffValidity
from datetime import date
from django.db.models import Q

def test_heating_norm():
    for heating_norm_validity in HeatingNormValidity.objects.all().order_by('start'):
        for heating_norm in HeatingNorm.objects.filter(validity=heating_norm_validity).order_by('floor_amount', 'commissioning_type'):
            norm = heating_norm.value

def test_water_tariff():
    for water_tariff_validity in WaterTariffValidity.objects.all().order_by('start'):
        pass
    
def test_db():
    subjectsRF = SubjectRF.objects.all()
    for subjectRF in subjectsRF:
        for municipal_area in MunicipalArea.objects.all():
            for municipal_union in MunicipalUnion.objects.all():
                for loc in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union).order_by('name'):
                    for street in Street.objects.filter(locality=loc).order_by('name'):
                        pass

def test_house_address():
    file = open('c:\\vitaly\\HouseNr.txt', 'w')
    
    subjectsRF = SubjectRF.objects.all()
    for subjectRF in subjectsRF:
        for municipal_area in MunicipalArea.objects.all():
            for municipal_union in MunicipalUnion.objects.all():
                for loc in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union).order_by('name'):
                    file.write(str(loc))
                    file.write("\n")
                    for street in Street.objects.filter(locality=loc).order_by('name'):
                        for house_nr in HouseAddress.objects.filter(street=street).order_by('house_number'):
                            file.write(str(house_nr))
                            file.write("\n")

    file.close()

def test_org_srv():
    for org_srv in OrganizationService.objects.all():
        pass

def test_real_estate():
    file = open('c:\\vitaly\\RealEstate.txt', 'w')
    
    subjectsRF = SubjectRF.objects.all()
    for subjectRF in subjectsRF:
        for municipal_area in MunicipalArea.objects.all():
            for municipal_union in MunicipalUnion.objects.all():
                for loc in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union).order_by('name'):
                    file.write(str(loc))
                    file.write("\n")
                    for street in Street.objects.filter(locality=loc).order_by('name'):
                        for address in HouseAddress.objects.filter(street=street).order_by('house_number'):
                            for real_estate in RealEstate.objects.filter(address=address):
                                file.write(str(real_estate))
                                file.write("\n")

    file.close()

def test_residents_degree():
    water_norm_validity = WaterNormValidity.objects.filter(start ='2015-01-01', end='2015-03-31').get()
    
    file = open('c:\\Vitaly\\Reading\\residents_degree.txt', 'r')
    file = open('c:\\Vitaly\\Reading\\residents_degree.txt', 'r')
    for line in file:
        index = 0
        locality_name = ""
        street_name = ""
        house_nr = ""
        number = ""
        residents = ""
        norm = ""
        for part in line.split("\t"):
            part.strip()
            if part == "\n" or len(part) == 0:
                index = index + 1
                continue
            
            if index == 0:
                locality_name = part
            elif index == 1:
                street_name = part
            elif index == 2:
                house_nr = part
            elif index == 3:
                number = part
            elif index == 4:
                residents = part
            elif index == 5:
                norm = part
            else:
                pass
            index = index + 1

        loc = Locality.objects.filter(name=locality_name).get()
        street = Street.objects.filter(locality=loc, name=street_name).get()
        address = HouseAddress.objects.filter(street=street, house_number=house_nr).get()
        count = 0
        if len(residents) != 0:
            count = int(residents)
        if len(norm) != 0:
            norm_value = float(norm)
            
            real_estate = RealEstate.objects.filter(address=address, number=number).get()
            water_desc = None
            if norm_value == 6.47 or norm_value == 6.0:
                water_desc = WaterNormDescription.objects.filter(description='Жилые помещения (в том числе общежития) с холодным водоснабжением, водонагревателями, канализованием, оборудованные ваннами, душами, раковинами, кухонными мойками и унитазами', type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING).get()
            else:
                if WaterNorm.objects.filter(validity=water_norm_validity, type=WaterType.COLD_WATER, value=norm_value).count() != 1:
                    pass
                water_norm = WaterNorm.objects.filter(validity=water_norm_validity, type=WaterType.COLD_WATER, value=norm_value).get()
                water_desc = water_norm.norm_description

            water_desc = None
    file.close()


def get_water_norm(subject_rf, water_description, period, water_type):
    # Получение периода действия норматива по расчетному периоду. Расчетный период устанавливается равным календарному месяцу. Поэтому, считаем, что за один месяц может быть только один норматив.
    validity = WaterNormValidity.objects.filter(start__lte=period.end).order_by('-start')[0]
    
    water_norm = WaterNorm.objects.filter(subject_rf=subject_rf, norm_description=water_description, validity=validity, type=water_type).get()
    return water_norm.value

def test_water_norm():
    for real_estate in RealEstate.objects.filter(Q(type=RealEstate.HOUSE) | Q(type=RealEstate.FLAT)):
        for period in Period.objects.all().order_by('serial_number'):
            pass
            #HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start='2014-12-26')real_estate
        
    for water_norm_desc in WaterNormDescription.objects.all():
        for water_norm_validity in WaterNormValidity.objects.all().order_by('start'):    
            for water_norm in WaterNorm.objects.filter(norm_description=water_norm_desc, validity=water_norm_validity, type=WaterType.COLD_WATER):
                pass

def get_client_water_description(real_estate, period):
    water_description = HomeownershipHistory.objects
    WaterNormDescription.objects.filter(type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING, ).get()


def get_residents(real_estate, period):
    """ Возвращает количество проживающих в 'real_estate' за расчетный период 'period'.
    Полагаем, что количество проживающих за один расчетный период постоянно. Если нужно будет учитывать не по расчетному периоду, а по дате, тогда возвращать кортеж: 'количество дней, количество проживающх'"""
    homeownership = HomeownershipHistory.objects.filter(Q(real_estate=real_estate) & Q(water_description__type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING) & Q(start__lte=period.end)).order_by('-start')[0]
    
    # Поле 'count' в таблице HomeownershipHistory имеет тип float. Преобразуем к целому.
    residents = int(homeownership.count)
    return residents

def calculate_individual_water_volume_by_norm(subject_rf, real_estate, period, water_type):
    """
    Функция расчета объема услуге по воде по нормативу потребления.
    Используется формула #4.
    """
    if real_estate.type == RealEstate.MUNICIPAL_BUILDING or real_estate.type == RealEstate.SHARE:
        raise Exception #TODO: Продумать ошибку (Для данного типа помещения нельзя расчитать объем. Расчет должен выполняться для внутренних помещений).
    
    # Метода используется только для жилых помещений. Дополнительная проверка на условия не проводится, т.к. здесь может присутствовать либо отстутствовать счетчик (эти условия должны выполняться в методах более высокого уровня)
    if real_estate.residential == False:
        raise Exception #TODO: Продумать ошибку (Вычисление норматива потребления должны вызываться только для жилых помещений).
    
    homeownership = HomeownershipHistory.objects.filter(Q(real_estate=real_estate) & Q(water_description__type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING) & Q(start__lte=period.end)).order_by('-start')[0]
    water_description = homeownership.water_description
    # Получаем количество проживающих.
    #residents = get_residents(real_estate, period)
    residents = int(homeownership.count)
    
    # Получаем норматив потребления
    norm = get_water_norm(subject_rf, water_description, period, water_type)
    
    volume = norm * residents
    return volume

def calculate_individual_water_volume(subject_rf, real_estate, calc_period, water_type):
    calculate_individual_water_volume_by_norm(subject_rf, real_estate, calc_period, water_type)

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
            service = client_service.service.service
            if service == Service.COLD_WATER:
                calculate_individual_water_volume(subject_rf, real_estate, calc_period, WaterType.COLD_WATER)
            elif service == Service.HOT_WATER:
                pass
            elif service == Service.HEATING:
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

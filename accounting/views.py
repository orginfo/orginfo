from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality
from accounting.models import Street, HouseAddress
from accounting.models import Organization
from accounting.models import RealEstate, HomeownershipHistory
from accounting.models import Service, ClientService, OrganizationService
from accounting.models import WaterNormDescription, WaterNormValidity, WaterNorm
from accounting.models import HeatingNormValidity, HeatingNorm
from accounting.models import WaterTariffValidity
from datetime import date

def test_water_norm():
    file = open('c:\\vitaly\\WaterNorm.txt', 'w')
    
    for water_norm_desc in WaterNormDescription.objects.all():
        for water_norm_validity in WaterNormValidity.objects.all().order_by('start'):    
            for water_norm in WaterNorm.objects.filter(norm_description=water_norm_desc, validity=water_norm_validity, type=WaterNorm.COLD_WATER_TYPE):
                norm = str(water_norm.value)
                norm += '\t'
                file.write(norm)
        file.write('\n')
    file.close()

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
                if WaterNorm.objects.filter(validity=water_norm_validity, type=WaterNorm.COLD_WATER_TYPE, value=norm_value).count() != 1:
                    pass
                water_norm = WaterNorm.objects.filter(validity=water_norm_validity, type=WaterNorm.COLD_WATER_TYPE, value=norm_value).get()
                water_desc = water_norm.norm_description

            water_desc = None
    file.close()

def calculate_individual_cold_water_volume(real_estate, calc_period):
    pass

def calculate_services(real_estate, calc_period):
    for client_service in ClientService.objects.filter(real_estate=real_estate).order_by('service'):
        service = Service.objects.filter(service=client_service).get()
        if service == Service.COLD_WATER:
            calculate_individual_cold_water_volume()
        elif service == Service.HOT_WATER:
            pass

def robot():
    calc_period = date.today() 
    for subjectRF in SubjectRF.objects.all():
        for municipal_area in MunicipalArea.objects.filter(subject_rf=subjectRF):
            for municipal_union in MunicipalUnion.objects.filter(municipal_area=municipal_area):
                for locality in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union):
                    for real_estate in RealEstate.objects.filter(address__street__locality=locality):
                        calculate_services(real_estate, calc_period)

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

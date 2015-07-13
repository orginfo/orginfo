from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality
from accounting.models import Street, HouseAddress
from accounting.models import RealEstate
from accounting.models import WaterNormDescription, WaterNormValidity, WaterNorm
from accounting.models import HeatingNormValidity, HeatingNorm
from accounting.models import WaterTariffValidity
from accounting.models import Organization, OrganizationService

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

def test_org():
    for org in Organization.objects.all():
        pass

def test_org_addr():
    loc = Locality.objects.filter(name="Кудельный Ключ").get()
    street_k = Street.objects.filter(locality=loc, name="Центральная").get()
    #ddress_k = HouseAddress.objects.filter(street=street_k, house_number="5").get()
    for house in HouseAddress.objects.filter(street=street_k):
        number = 6

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

def index(request):
    #test_db()
    #test_heating_norm()
    #test_water_tariff()
    #test_service()
    #test_house_address()
    #test_org()
    #test_org_addr()
    #test_org_srv()
    test_real_estate()
    return HttpResponse("Робот отработал успешно.")

from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality, Street
from accounting.models import WaterNormDescription, WaterNormValidity, WaterNorm
from accounting.models import HeatingNormValidity, HeatingNorm
from accounting.models import WaterTariffValidity

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

def index(request):
    #test_db()
    #test_heating_norm()
    test_water_tariff()
    return HttpResponse("Робот отработал успешно.")

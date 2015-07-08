from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality, Street, WaterNormDescription, WaterNormValidity

def test_norm():
    for water_norm_desc in WaterNormDescription.objects.all():
        desc = water_norm_desc.description
        type = water_norm_desc.type

    for water_norm_validity in WaterNormValidity.objects.all().order_by('start'):
        pass
    """
    for subjectRF in SubjectRF.objects.all():
        for municipal_area in MunicipalArea.objects.all():
    """

def test_db():
    subjectsRF = SubjectRF.objects.all()
    for subjectRF in subjectsRF:
        for municipal_area in MunicipalArea.objects.all():
            for municipal_union in MunicipalUnion.objects.all():
                for loc in Locality.objects.filter(municipal_area=municipal_area, municipal_union=municipal_union).order_by('name'):
                    for street in Street.objects.filter(locality=loc).order_by('name'):
                        pass
    test_norm()

def index(request):
    test_db()
    return HttpResponse("Робот отработал успешно.")

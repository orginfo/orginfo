from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion

def test_db():
    subjectsRF = SubjectRF.objects.all()
    for subjectRF in subjectsRF:
        name = subjectRF.name
        for municipal_area in MunicipalArea.objects.all():
            for municipal_union in MunicipalUnion.objects.all():
                name = municipal_union.name

def index(request):
    test_db()
    return HttpResponse("Робот отработал успешно.")

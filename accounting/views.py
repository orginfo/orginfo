from django.http import HttpResponse
from accounting.models import SubjectRF, MunicipalArea

def write_of():
    subjectsRF = SubjectRF.objects.all()
    for subjectRF in subjectsRF:
        name = subjectRF.name
        for municipal_area in MunicipalArea.objects.all():
            pass

def index(request):
    write_of()
    return HttpResponse("Робот отработал успешно.")

from django.http import HttpResponse
from accounting.models import SubjectRF

def write_of():
    subjectsRF = SubjectRF.objects.all()
    for subjectRF in subjectsRF:
        name = subjectRF.name

def index(request):
    write_of()
    return HttpResponse("Робот отработал успешно.")

from django.http import HttpResponse

def index(request):
    return HttpResponse("Робот отработал успешно.")
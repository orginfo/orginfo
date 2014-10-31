from django.shortcuts import render

def validate(request):
    return render(request, 'accounting/index.html', {})

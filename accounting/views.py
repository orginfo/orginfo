from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from accounting.forms import OrganizationForm
from django.contrib.auth.models import User
from accounting.models import Organization

@login_required(login_url="/login/")
def index(request):
    return render(request, 'accounting/index.html', {})

def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            user = User.objects.create_user(username, 'no@mail.com', password)
            user.save()
            organization = Organization.objects.create(name=name, user_id=user)
            organization.save()
            return HttpResponseRedirect(reverse('accounting:index'))
    else:
        form = OrganizationForm()

    return render(request, 'accounting/organization.html', {
        'form': form,
    })

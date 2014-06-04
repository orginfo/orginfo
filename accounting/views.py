from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from accounting.forms import OrganizationForm
from django.contrib.auth.models import User
from accounting.models import Organization, UserOrganization

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
            organization = Organization.objects.create(name=name, user=user)
            organization.save()
            return HttpResponseRedirect(reverse('accounting:index'))
    else:
        form = OrganizationForm()

    return render(request, 'accounting/organization.html', {
        'form': form,
    })

@login_required(login_url="/login/")
def organization_details(request):
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            if user_org.organization:
                user_org.organization.name = form.cleaned_data['name']
                user_org.organization.save()
            else:
                organization = Organization.objects.create(name=form.cleaned_data['name'])
                organization.save()
                user_org.organization = organization
                user_org.save()
            return HttpResponseRedirect(reverse('accounting:organization_details'))
    else:
        if user_org.organization:
            data = {}
            org = user_org.organization
            data['name'] = org.name
            form = OrganizationForm(data)
        else:
            form = OrganizationForm()

    return render(request, 'accounting/organization.html', {
        'form': form,
    })

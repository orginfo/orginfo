from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from accounting.forms import OrganizationForm
from accounting.models import Organization, UserOrganization, Client

@login_required(login_url="/login/")
def index(request):
    return render(request, 'accounting/index.html', {})

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

@login_required(login_url="/login/")
def clients(request):
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    clients = Client.objects.filter(organization=user_org.organization_id)
    return render(request, 'accounting/clients.html', {'clients': clients})

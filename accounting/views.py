from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from accounting.forms import OrganizationForm#, LastNameSearchForm
from accounting.models import Organization, UserOrganization, Client, Payment
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django import forms


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

class TakePayment(CreateView):
    model = Payment
    template_name = 'accounting/take_payment.html'
    fields = ['amount']
    exclude = ('client',)
    def dispatch(self, *args, **kwargs):
        user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        clients = user_org.organization.client_set.all()
        client_id = int(kwargs['client_id'])
        self.client = next((client for client in clients if client.id==client_id), None)
        if not self.client:
            raise Http404
        return super(TakePayment, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
         form.instance.client = self.client
         return super(TakePayment, self).form_valid(form)
    def get_context_data(self, **kwargs):
        context = super(TakePayment, self).get_context_data(**kwargs)
        context['client'] = self.client
        return context

class FindClients(ListView):
    class LastNameSearchForm(forms.Form):
        #name = forms.CharField(required=False)
        name = forms.CharField(max_length=3, required=False)
    form_class = LastNameSearchForm
    def dispatch(self, *args, **kwargs):
        self.form = self.form_class(self.request.GET)
        self.user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        return super(FindClients, self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(FindClients, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context
    def get_queryset(self):
        if self.form.is_valid():
            name = self.form.cleaned_data['name']
            object_list = self.user_org.organization.client_set.filter(lfm__icontains = name)
        else:
            object_list = self.user_org.organization.client_set.none()
        return object_list

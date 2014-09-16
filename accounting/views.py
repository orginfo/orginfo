from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from accounting.forms import OrganizationForm, ExampleForm, LastNameSearchForm, CreateClientForm, CreateRealEstateForm, CreateColdWaterReadingForm
from accounting.models import Organization, UserOrganization, Client, Payment, RealEstate, ColdWaterReading
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from robot.algorithm import write_off


@login_required(login_url="/login/")
def index(request):
    return render(request, 'accounting/index.html', {})

def robot(request):
    write_off()
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

class TakePayment(CreateView):
    form_class = ExampleForm
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

class Clients(ListView):
    form_class = LastNameSearchForm
    context_object_name = 'clients'
    template_name = 'accounting/clients.html'
    def dispatch(self, *args, **kwargs):
        self.form = self.form_class(self.request.GET)
        self.user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        return super(Clients, self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(Clients, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context
    def get_queryset(self):
        if self.form.is_valid():
            name = self.form.cleaned_data['name']
            object_list = self.user_org.organization.client_set.filter(lfm__icontains = name)
        else:
            object_list = self.user_org.organization.client_set.none()
        return object_list

class CreateClient(CreateView):
    form_class = CreateClientForm
    model = Client
    template_name = 'accounting/add_client.html'
    exclude = ('organization',)
    fields = ['lfm', 'amount', 'real_estate', 'residential', 'residents']
    def dispatch(self, *args, **kwargs):
        user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        if not user_org.organization:
            raise Http404
        self.organization = user_org.organization
        return super(CreateClient, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        form.instance.organization = self.organization
        return super(CreateClient, self).form_valid(form)

class UpdateClient(UpdateView):
    form_class = CreateClientForm
    model = Client
    template_name = 'accounting/add_client.html'
    exclude = ('organization',)
    fields = ['lfm', 'amount', 'real_estate', 'residential', 'residents']
    def dispatch(self, *args, **kwargs):
        user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        if not user_org.organization:
            raise Http404
        self.organization = user_org.organization
        return super(UpdateClient, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        form.instance.organization = self.organization
        return super(UpdateClient, self).form_valid(form)

def report(request):
    "the last payment in the organization"
    user_org = get_object_or_404(UserOrganization, user=request.user.id)
    if not user_org.organization:
        raise Http404
    last_payment = Payment.objects.filter(client__organization=user_org.organization).last()
    context = {
        'last_payment': last_payment,
        'period': '2014-06-01 (TODO)'
    }
    return render(request, 'accounting/report.html', context)

class CreateRealEstate(CreateView):
    model = RealEstate
    template_name = 'accounting/add_client.html'
    form_class = CreateRealEstateForm

class ColdWaterReadings(ListView):
    model = ColdWaterReading
    template_name = 'accounting/cold_water_readings.html'
    context_object_name = 'readings'
    def get_queryset(self):
        return ColdWaterReading.objects.filter(real_estate=self.kwargs['real_estate_id']);
    def get_context_data(self, **kwargs):
        context = super(ColdWaterReadings, self).get_context_data(**kwargs)
        context['url_to_create'] = reverse('accounting:create_reading', kwargs=self.kwargs)
        return context

class CreateColdWaterReading(CreateView):
    model = ColdWaterReading
    form_class = CreateColdWaterReadingForm
    template_name = 'accounting/add_client.html'
    def get_success_url(self):
        return reverse('accounting:readings', kwargs=self.kwargs)


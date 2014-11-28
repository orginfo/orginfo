from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from accounting.forms import OrganizationForm, ExampleForm, LastNameSearchForm, CreateRealEstateForm, CreateColdWaterReadingForm, CreateClientServiceForm, CreateServiceUsageForm, CreateAccountForm, CreatePaymentForm, WhatAccountForm
from accounting.models import Organization, UserOrganization, Payment, RealEstate, ColdWaterReading, ServiceClient, Account
from django.views.generic.edit import CreateView, UpdateView, FormView
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
                user_org.organization.address = form.cleaned_data['address']
                user_org.organization.rs = form.cleaned_data['rs']
                user_org.organization.ks = form.cleaned_data['ks']
                user_org.organization.bik = form.cleaned_data['bik']
                user_org.organization.inn = form.cleaned_data['inn']
                user_org.organization.phone = form.cleaned_data['phone']
                user_org.organization.fax = form.cleaned_data['fax']
                user_org.organization.email = form.cleaned_data['email']
                user_org.organization.operation_mode = form.cleaned_data['operation_mode']
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
            data['address'] = org.address
            data['rs'] = org.rs
            data['ks'] = org.ks
            data['bik'] = org.bik
            data['inn'] = org.inn
            data['phone'] = org.phone
            data['fax'] = org.fax
            data['email'] = org.email
            data['operation_mode'] = org.operation_mode
            form = OrganizationForm(data)
        else:
            form = OrganizationForm()

    return render(request, 'accounting/organization.html', {
        'form': form,
    })

class RealEstates(ListView):
    form_class = LastNameSearchForm
    context_object_name = 'real_estates'
    template_name = 'accounting/real_estates.html'
    def dispatch(self, *args, **kwargs):
        self.form = self.form_class(self.request.GET)
        self.user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        return super(RealEstates, self).dispatch(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(RealEstates, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context
    def get_queryset(self):
        if self.form.is_valid():
            name = self.form.cleaned_data['name']
            object_list = RealEstate.objects.filter(address__icontains = name, organization=self.user_org.organization)
        else:
            object_list = RealEstate.objects.none()
        return object_list

class CreateRealEstate(CreateView):
    form_class = CreateRealEstateForm
    model = RealEstate
    template_name = 'accounting/add_client.html'
    exclude = ('organization', 'parent')
    def dispatch(self, *args, **kwargs):
        user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        if not user_org.organization:
            raise Http404
        self.organization = user_org.organization
        return super(CreateRealEstate, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        form.instance.organization = self.organization
        parent_street = form.cleaned_data['parent_street']
        if parent_street is '':
            form.instance.parent = None
        else:
            form.instance.parent = RealEstate.objects.filter(address=parent_street, organization=self.organization).get()
        return super(CreateRealEstate, self).form_valid(form)

class UpdateRealEstate(UpdateView):
    form_class = CreateRealEstateForm
    model = RealEstate
    template_name = 'accounting/update_real_estate.html'
    exclude = ('organization', 'parent')
    def dispatch(self, *args, **kwargs):
        user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        if not user_org.organization:
            raise Http404
        self.organization = user_org.organization
        return super(UpdateRealEstate, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        form.instance.organization = self.organization
        parent_street = form.cleaned_data['parent_street']
        if parent_street is '':
            form.instance.parent = None
        else:
            form.instance.parent = RealEstate.objects.filter(address=parent_street, organization=self.organization).get()
        return super(UpdateRealEstate, self).form_valid(form)
    def get_initial(self):
        initial = super(UpdateRealEstate, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        initial = initial.copy()
        initial['parent_street'] = ''
        if self.object.parent is not None:
            initial['parent_street'] = self.object.parent.address
        return initial
    def get_context_data(self, **kwargs):
        context = super(UpdateRealEstate, self).get_context_data(**kwargs)
        context['real_estate_id'] = self.kwargs['pk']
        return context

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

class ColdWaterReadings(ListView):
    model = ColdWaterReading
    template_name = 'accounting/cold_water_readings.html'
    context_object_name = 'readings'
    def get_queryset(self):
        return ColdWaterReading.objects.filter(real_estate=self.kwargs['real_estate_id']);
    def get_context_data(self, **kwargs):
        context = super(ColdWaterReadings, self).get_context_data(**kwargs)
        context['real_estate_id'] = self.kwargs['real_estate_id']
        return context

class CreateColdWaterReading(CreateView):
    model = ColdWaterReading
    form_class = CreateColdWaterReadingForm
    template_name = 'accounting/cold_water_reading.html'
    def get_success_url(self):
        return reverse('accounting:readings', kwargs=self.kwargs)
    def form_valid(self, form):
        form.instance.real_estate_id = self.kwargs['real_estate_id']
        return super(CreateColdWaterReading, self).form_valid(form)

class UpdateColdWaterReading(UpdateView):
    model = ColdWaterReading
    form_class = CreateColdWaterReadingForm
    template_name = 'accounting/cold_water_reading.html'
    def get_success_url(self):
        return reverse('accounting:readings', kwargs={'real_estate_id': self.kwargs['real_estate_id']})
    def form_valid(self, form):
        form.instance.real_estate_id = self.kwargs['real_estate_id']
        return super(UpdateColdWaterReading, self).form_valid(form)

class ServiceUsages(ListView):
    model = ServiceClient
    template_name = 'accounting/service_usages.html'
    context_object_name = 'services'
    def get_queryset(self):
        return ServiceClient.objects.filter(real_estate=self.kwargs['real_estate_id']);
    def get_context_data(self, **kwargs):
        context = super(ServiceUsages, self).get_context_data(**kwargs)
        context['real_estate_id'] = self.kwargs['real_estate_id']
        return context

class CreateServiceUsage(CreateView):
    model = ServiceClient
    template_name = 'accounting/add_client.html'
    form_class = CreateServiceUsageForm
    def get_success_url(self):
        return reverse('accounting:service_usages', kwargs=self.kwargs)
    def form_valid(self, form):
        form.instance.real_estate_id = self.kwargs['real_estate_id']
        return super(CreateServiceUsage, self).form_valid(form)

class UpdateServiceUsage(UpdateView):
    model = ServiceClient
    form_class = CreateServiceUsageForm
    template_name = 'accounting/add_client.html'
    def get_success_url(self):
        return reverse('accounting:service_usages', kwargs={'real_estate_id': self.kwargs['real_estate_id']})
    def form_valid(self, form):
        form.instance.real_estate_id = self.kwargs['real_estate_id']
        return super(UpdateServiceUsage, self).form_valid(form)

class Accounts(ListView):
    model = Account
    template_name = 'accounting/accounts.html'
    context_object_name = 'accounts'
    def get_queryset(self):
        return Account.objects.filter(real_estate=self.kwargs['real_estate_id']);
    def get_context_data(self, **kwargs):
        context = super(Accounts, self).get_context_data(**kwargs)
        context['real_estate_id'] = self.kwargs['real_estate_id']
        return context

class CreateAccount(CreateView):
    model = Account
    template_name = 'accounting/add_client.html'
    form_class = CreateAccountForm
    def get_success_url(self):
        return reverse('accounting:accounts', kwargs=self.kwargs)
    def form_valid(self, form):
        form.instance.real_estate_id = self.kwargs['real_estate_id']
        return super(CreateAccount, self).form_valid(form)

class UpdateAccount(UpdateView):
    model = Account
    form_class = CreateAccountForm
    template_name = 'accounting/add_client.html'
    def get_success_url(self):
        return reverse('accounting:accounts', kwargs={'real_estate_id': self.kwargs['real_estate_id']})
    def form_valid(self, form):
        form.instance.real_estate_id = self.kwargs['real_estate_id']
        return super(UpdateAccount, self).form_valid(form)

class Payments(ListView):
    model = Payment
    template_name = 'accounting/payments.html'
    context_object_name = 'payments'
    def dispatch(self, *args, **kwargs):
        user_org = get_object_or_404(UserOrganization, user=self.request.user.id)
        if not user_org.organization:
            raise Http404
        real_estate = get_object_or_404(RealEstate, id=self.kwargs['real_estate_id'], organization=user_org.organization)
        real_estate_accounts = real_estate.account_set.all()
        account_choices = []
        last_account_id = None
        for account in real_estate_accounts:
            account_choices.append((account.id, account.owners),)
            last_account_id = account.id

        account_id = None
        form = WhatAccountForm(account_choices, self.request.GET) #TODO: if empty choices
        if form.is_valid():
            account_id = last_account_id
            if form.cleaned_data['name'] is not '':
                account_id = form.cleaned_data['name']
        else:
            raise Http404
        self.account_id = account_id

        self.form = WhatAccountForm(account_choices, {'name': account_id}) #TODO: account_id instead of GET
        return super(Payments, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        if self.account_id:
            payments = Payment.objects.filter(account_id=self.account_id)
        else:
            payments = Payment.objects.none()
        return payments
    def get_context_data(self, **kwargs):
        context = super(Payments, self).get_context_data(**kwargs)
        context['real_estate_id'] = self.kwargs['real_estate_id']
        context['account_id'] = self.account_id
        context['form'] = self.form
        return context

class CreatePayment(FormView):
    template_name = 'accounting/add_client.html'
    form_class = CreatePaymentForm
    def get_success_url(self):
        return "%s?name=%s" % (reverse('accounting:payments', kwargs={'real_estate_id': self.kwargs['real_estate_id']}), self.kwargs['account_id'])
    def form_valid(self, form):
        #TODO: нет защиты от не своего.
        #TODO: не в транзакции.
        account = get_object_or_404(Account, id=self.kwargs['account_id'])

        payment = Payment(
                amount=form.cleaned_data['amount'],
                balance_before_payment = account.balance,
                account=account,
                date=form.cleaned_data['date'],
                comment=form.cleaned_data['comment'])
        payment.save()

        account.balance = account.balance + form.cleaned_data['amount']
        account.save()

        return super(CreatePayment, self).form_valid(form)

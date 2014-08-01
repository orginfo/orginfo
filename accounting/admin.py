from django.contrib import admin
from accounting.models import Organization, UserOrganization, Client, RealEstate, Payment, ServiceClient, ColdWaterCounter, ColdWaterValue, ColdWaterTariff

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('lfm', 'organization', 'amount')

class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization')

class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('address', 'parent')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'client', 'real_estate')

class ServiceClientAdmin(admin.ModelAdmin):
    list_display = ('client', 'service_name')

class ColdWaterCounterAdmin(admin.ModelAdmin):
    list_display = ('value', 'real_estate', 'date')

class ColdWaterValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'real_estate', 'date')

class ColdWaterTariffAdmin(admin.ModelAdmin):
    list_display = ('client', 'value')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(RealEstate, RealEstateAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ServiceClient, ServiceClientAdmin)
admin.site.register(ColdWaterCounter, ColdWaterCounterAdmin)
admin.site.register(ColdWaterValue, ColdWaterValueAdmin)
admin.site.register(ColdWaterTariff, ColdWaterTariffAdmin)

from django.contrib import admin
from accounting.models import Organization, UserOrganization, Client, RealEstate, Payment, ServiceClient, ColdWaterReading, ColdWaterVolume, ColdWaterTariff, Period

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

class PeriodAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'start', 'end')

class ColdWaterReadingAdmin(admin.ModelAdmin):
    list_display = ('period', 'value', 'real_estate', 'date')

class ColdWaterVolumeAdmin(admin.ModelAdmin):
    list_display = ('period', 'value', 'real_estate', 'date')

class ColdWaterTariffAdmin(admin.ModelAdmin):
    list_display = ('client', 'value')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(RealEstate, RealEstateAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ServiceClient, ServiceClientAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(ColdWaterReading, ColdWaterReadingAdmin)
admin.site.register(ColdWaterVolume, ColdWaterVolumeAdmin)
admin.site.register(ColdWaterTariff, ColdWaterTariffAdmin)

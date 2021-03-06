from django.contrib import admin
from accounting.models import Organization, UserOrganization, RealEstate, Payment, ServiceClient, ColdWaterReading, ColdWaterVolume, ColdWaterTariff, Period, Region, ColdWaterNorm, Account

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('lfm',)

class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization')

class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('address', 'parent')

class PeriodAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'start', 'end')

class ColdWaterReadingAdmin(admin.ModelAdmin):
    list_display = ('period', 'value', 'real_estate', 'date')

class ColdWaterVolumeAdmin(admin.ModelAdmin):
    list_display = ('period', 'volume', 'real_estate', 'date')

class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(RealEstate, RealEstateAdmin)
admin.site.register(Payment)
admin.site.register(ServiceClient)
admin.site.register(Period, PeriodAdmin)
admin.site.register(ColdWaterReading, ColdWaterReadingAdmin)
admin.site.register(ColdWaterVolume, ColdWaterVolumeAdmin)
admin.site.register(ColdWaterTariff)
admin.site.register(Region, RegionAdmin)
admin.site.register(ColdWaterNorm)
admin.site.register(Account)

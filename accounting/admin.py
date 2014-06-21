from django.contrib import admin
from accounting.models import Organization, UserOrganization, Client, RealEstate, Payment

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('lfm', 'organization')

class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization')

class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('address', 'parent')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'client', 'real_estate')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(RealEstate, RealEstateAdmin)
admin.site.register(Payment, PaymentAdmin)

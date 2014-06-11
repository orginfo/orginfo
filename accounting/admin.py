from django.contrib import admin
from accounting.models import Organization, UserOrganization, Client, Payment

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('lfm', 'organization')

class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'client')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Payment, PaymentAdmin)

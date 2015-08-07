from django.contrib import admin
from accounting.models import UserOrganization, Account

class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization')
admin.site.register(UserOrganization, UserOrganizationAdmin)

#TODO: delete. Завожу для теста 2 раздела.
class AccountAdmin(admin.ModelAdmin):
    list_display = ("real_estate", "balance", "operation_type", "operation_date", "amount")
admin.site.register(Account, AccountAdmin)

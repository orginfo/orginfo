from django.contrib import admin
from accounting.models import UserOrganization, AccountOperation, Counter

class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization')
admin.site.register(UserOrganization, UserOrganizationAdmin)

#TODO: delete. Завожу для теста 2 раздела.
class AccountOperationAdmin(admin.ModelAdmin):
    list_display = ("real_estate", "balance", "operation_type", "operation_date", "amount")
admin.site.register(AccountOperation, AccountOperationAdmin)

#TODO: delete.
class CounterAdmin(admin.ModelAdmin):
    list_display = ("number", "service", "real_estate", "unit_type", "start", "end")
admin.site.register(Counter, CounterAdmin)

from django.contrib import admin
from accounting.models import UserOrganization

class UserOrganizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization')
admin.site.register(UserOrganization, UserOrganizationAdmin)

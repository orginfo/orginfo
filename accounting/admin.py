from django.contrib import admin
from accounting.models import Organization, UserOrganization
 
admin.site.register(Organization)
admin.site.register(UserOrganization)

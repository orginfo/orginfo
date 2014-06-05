from django.db import models
from django.contrib.auth.models import User

class Organization(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class UserOrganization(models.Model):
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization, null=True, blank=True, default = None)

class Client(models.Model):
    lfm = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization)

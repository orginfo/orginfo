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
    def __str__(self):
        return self.lfm + "(" + self.organization.__str__() + ")"

class RealEstate(models.Model):
    address = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, default = None)
    def __str__(self):
        return self.address

class Payment(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    client = models.ForeignKey(Client)
    real_estate = models.ForeignKey(RealEstate, null=True, blank=True, default = None)

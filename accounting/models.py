from django.db import models

class SubjectRF(models.Model):
    """ СУбъект РФ """
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class MunicipalArea(models.Model):
    """ Муниципальный район """
    name = models.CharField(max_length=20)
    subject_rf = models.ForeignKey(SubjectRF)
    def __str__(self):
        return "%s, %s" % (self.subject_rf.name, self.name)

class MunicipalUnion(models.Model):
    """ Муниципальное образование """
    name = models.CharField(max_length=50)
    municipal_area = models.ForeignKey(MunicipalArea)
    def __str__(self):
        return "%s, %s, %s" % (self.municipal_area.subject_rf.name, self.municipal_area.name, self.name)

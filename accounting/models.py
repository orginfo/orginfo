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

class Locality(models.Model):
    """ Населенный пункт """
    
    CITY = '1'
    VILLAGE = '2'
    RAILROAD_SIDING = '3'
    RAILWAY_STATION = '4'
    WAYSIDE_STOP = '5'
    SETTLEMENT = '6'
    INDUSTRIAL_SETTLEMENT = '7'
    HAMLET = '8'
    
    TYPE = (
        (CITY, 'город'),
        (VILLAGE, 'деревня'),
        (RAILROAD_SIDING, 'железнодорожный разъезд'),
        (RAILWAY_STATION, 'железнодорожная станция'),
        (WAYSIDE_STOP, 'остановочная платформа'),
        (SETTLEMENT, 'посёлок'),
        (INDUSTRIAL_SETTLEMENT, 'рабочий посёлок'),
        (HAMLET, 'село'),
    )
    
    name = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=TYPE, default=HAMLET)
    municipal_area = models.ForeignKey(MunicipalArea)
    municipal_union = models.ForeignKey(MunicipalUnion)
    def __str__(self):
        return "%s, %s, %s %s" % (self.municipal_area.subject_rf.name, self.municipal_area.name, self.get_type_display(), self.name)

class Street(models.Model):
    """ Улица """
    
    STREET = '1'
    SIDE_STREET = '2'
    TYPE = (
        (STREET, 'улица'),
        (SIDE_STREET, 'переулок'),
    )
    
    name = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=TYPE, default=STREET)
    locality = models.ForeignKey(Locality)
    def __str__(self):
        return "%s %s" % (self.get_type_display(), self.name)

"""Данные для норматива по воде"""
class WaterNormDescription(models.Model):
    """Описание названий видов нормативов для воды (холодная, горячая, водоотведение)"""
    
    DEGREE_OF_IMPROVEMENT_DWELLING = '1'
    COMMON_PROPERTY = '2'
    AGRICULTURAL_ANIMALS = '3'
    DIRECTION_USING = '4'
    
    
    DESCRIPTION_TYPES = (
        (DEGREE_OF_IMPROVEMENT_DWELLING, 'Степень благоустройства жилых помещений'),
        (COMMON_PROPERTY, 'Общее имущество'),
        (AGRICULTURAL_ANIMALS, 'Виды сельскохозяйственных животных'),
        (DIRECTION_USING, 'Направления использования'),
    )
    
    description = models.TextField()
    type = models.CharField(max_length=1, choices=DESCRIPTION_TYPES, default=DEGREE_OF_IMPROVEMENT_DWELLING)
    
    def __str__(self):
        return "%s: %s" % (self.get_type_display(), self.description)
    
class WaterNormValidity(models.Model):
    """ Период действия норматива
    start - дата, с которой начинает действовать норматив
    end - дата окончания действия норматива
    """
    start = models.DateField()
    end = models.DateField()
    def __str__(self):
        return "%s->%s" % (str(self.start), str(self.end))

class WaterNorm(models.Model):
    """ Нормаnив по холодному, горячему водоснабжению и водоотведению.
    type - тип (холодное водоснабжение | горячее водоснабжение | водоотведение)
    value - норматив
    """
    COLD_WATER_TYPE = '1'
    HOT_WATER_TYPE = '2'
    WATER_DISPOSAL_TYPE = '3'
    WATER_TYPES = (
        (COLD_WATER_TYPE, 'Холодное водоснабжение'),
        (HOT_WATER_TYPE, 'Горячее водоснабжение'),
        (WATER_DISPOSAL_TYPE, 'Водоотведение'),
    )
    subject_fr = models.ForeignKey(SubjectRF)
    norm_description = models.ForeignKey(WaterNormDescription)
    validity = models.ForeignKey(WaterNormValidity)
    type = models.CharField(max_length=1, choices=WATER_TYPES, default=COLD_WATER_TYPE)
    value = models.FloatField()
    
    def __str__(self):
        return "%s\t%s\t%f" % (self.norm_description.description, self.get_type_display(), self.value)
"""\Данные для норматива по воде"""

"""Данные для норматива по отоплению"""
class HeatingNormValidity(models.Model):
    """ Период действия норматива для отопления
    start - дата, с которой начинает действовать норматив
    end - дата окончания действия норматива
    """
    start = models.DateField()
    end = models.DateField()
    def __str__(self):
        return "%s->%s" % (str(self.start), str(self.end))
"""\Данные для норматива по отоплению"""

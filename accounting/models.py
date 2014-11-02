from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Organization(models.Model):
    """Организация.

    МУП - это частный случай организации, поэтому МУП находится в этой модели.
    """
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class UserOrganization(models.Model):
    """Связь пользователь-организация.

    Пользователи бывают администраторами, клиентами организации, работниками
    организации. Связь показывает какой именно пользователь сайта является
    работником организации.
    """
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization, null=True, blank=True, default = None)

class RealEstate(models.Model):
    """Объект недвижимости.

    Объектом недвижимости может являться многоквартирный дом, жилой дом,
    квартира, комната. При этом у модели есть связь, которая показывает,
    например, какая именно комната принадлежит какой именно квартире.

    cold_water_counter_setup_date -- это дата установки счетчика холодной
    воды. Не совсем понятна ситуация со сменой счетчиков, т.е. должна ли
    находится информация cold_water_counter_setup_date именно в объекте
    недвижимости.
    """
    FLAT_TYPE = 'f'
    ROOM_TYPE = 'r'
    HOUSE_TYPE = 'h'
    BUILDING_TYPE = 'b'
    SHARE_TYPE = 's'
    REAL_ESTATE_TYPES = (
        (FLAT_TYPE, 'Flat'),
        (ROOM_TYPE, 'Room'),
        (HOUSE_TYPE, 'House'),
        (BUILDING_TYPE, 'Building'),
        (SHARE_TYPE, 'Share'),
    )

    address = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, default = None)
    cold_water_counter_setup_date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=1, choices=REAL_ESTATE_TYPES, default=HOUSE_TYPE)
    def __str__(self):
        return self.address

class TypeWaterNorm(models.Model):
    """Нормативы потребления коммунальных услуг по холодному водоснабжению, горячему водоснабжению и водоотведению
       в жилых помещениях на территории Новосиирской области.
       из "Приложение № 1 к приказу департамента по тарифам Новосибирской области".
       
       improvement_status - Степень благоустройства жилых помещений.
       
    """
    improvement_status = models.CharField(max_length=500)
    cold_water_norm = models.FloatField()
    hot_water_norm = models.FloatField()
    disposal_water_norm = models.FloatField()

class Client(models.Model):
    """Клиент.

    Клиент принадлежит организации, которая предоставляет ему услуги.
    У клиента есть свой лицевой счет, который характеризуется его номером,
    сейчас это ID клиента, и суммой на лицевом счете. Лицевой счет
    инкапсулирован в понятие клиента.
    TODO: со временем перенести поля residential residents в отдельную
    таблицу, потому что эта информация может меняться, а иногда полезно делать
    перерасчет, но информация, возможна будет потеряна.
    residential -- флаг, указывающий жилое ли помещение. Находится здесь,
    потому что как используется помещение зависит больше от клиента, а не от
    помещения.
    
    amount - сумма денег на счете клиента
    residents - количество зарегестированных (проживающих)
    """
    lfm = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    real_estate = models.ForeignKey(RealEstate)
    residential = models.BooleanField(default=True)
    residents = models.IntegerField(default=-1)
    #TODO: разобраться почему происходит 
    #You are trying to add a non-nullable field 'type_water_norm' to client without a default;
    #MAYBE: Удалить папку migrations.
    #type_water_norm = models.ForeignKey(TypeWaterNorm, null=True, blank=True, default = None)
    type_water_norm = models.ForeignKey(TypeWaterNorm)
    def __str__(self):
        return self.lfm + "(" + self.organization.__str__() + ")"
    def get_absolute_url(self):
        return reverse('accounting:client_update', kwargs={'pk': self.pk})

class Payment(models.Model):
    """Платеж.

    Платеж увеличивает сумму на лицевом счете клиента.
    TODO: Текущая модель рабочая, но не актуальная.
    """
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    client = models.ForeignKey(Client)
    real_estate = models.ForeignKey(RealEstate, null=True, blank=True, default = None)

class ServiceClient(models.Model):
    """Связь услуга-клиент.

    Связь указывает на то, какая именно услуга потребляется определенным
    клиентом. Альтернатива выставить флаг в модели Client, но тогда не сможем
    отключать услугу, выставлять ее время.
    """
    COLD_WATER_SERVICE = 'COLD_WATER_SERVICE'
    HOT_WATER_SERVICE = 'HOT_WATER_SERVICE'
    SERVICE_NAMES = (
        (COLD_WATER_SERVICE, 'Cold water'),
        (HOT_WATER_SERVICE, 'Hot water'),
    )
    client = models.ForeignKey(Client)
    service_name = models.CharField(max_length=100, choices=SERVICE_NAMES, default=COLD_WATER_SERVICE)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)

class Period(models.Model):
    """Расчетный период.

    В алгоритме робота возникла неоднозначность из-за даты проведения расчета.
    На нее ровняться не следует, т.к. она находится вне расчетного периода,
    который обсчитан по этой дате.

    Если вводить даты периода здесь, то будет довольно большая избыточность.
    К тому же нужна сущность что бы связать сущности:
    - объем услуги
    - пересчитанный объем услуги
    - показание счетчика
    Наличие сущности период, на которую завязаны вышеописанные сущности, решит
    вышеописанную проблему.
    Введение периода усложняет алгоритм, если расчитывать не относительно этого
    термина, а относительно дат.

    serial_number -- порядковый номер периода. Этим номером проходит сквозная
    нумерация всех периодов.

    start, end -- даты начала и конца периода соответсвенно.
    """
    serial_number = models.IntegerField()
    start = models.DateField()
    end = models.DateField()
    def __str__(self):
        return "#%s(%s->%s)" % (str(self.serial_number), str(self.start), str(self.end))

class ColdWaterReading(models.Model):
    """Показания приборов учета холодной воды.

    """
    period = models.ForeignKey(Period)
    value = models.FloatField()
    real_estate = models.ForeignKey(RealEstate)
    date = models.DateField()
    def __str__(self):
        return "%s: %s" % (str(self.period), str(self.value))

class ColdWaterVolume(models.Model):
    """Вычисления объема потребления холодной воды.

    """
    period = models.ForeignKey(Period)
    volume = models.FloatField()
    real_estate = models.ForeignKey(RealEstate)
    date = models.DateField()
    def __str__(self):
        return str(self.date)

class ColdWaterTariff(models.Model):
    """Тариф по услуге холодного водоснабжения для конкретного клиента."""
    client = models.ForeignKey(Client)
    value = models.IntegerField()
    def __str__(self):
        return "%s %s" % (str(self.client), self.value)

class AnimalType(models.Model):
    """Тип сельскохозяйственных животных."""
    name = models.CharField(max_length=200)
    norm = models.FloatField();
    def __str__(self):
        return "%s %s" % (self.name, str(self.norm))

class Animals(models.Model):
    """Сельскохозяйственные животные для всех домовладений."""
    count = models.IntegerField(default=-1)
    real_estate = models.ForeignKey(RealEstate)
    type = models.ForeignKey(AnimalType)

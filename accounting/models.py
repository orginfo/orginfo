from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Organization(models.Model):
    """Организация.

    МУП - это частный случай организации, поэтому МУП находится в этой модели.
    Адрес
    Банковские реквезиты (р/с, к/с, БИК)
    ИНН
    Телефон, факс, адрес электронной почты
    Режим работы
    """
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    rs = models.CharField(max_length=200)
    ks = models.CharField(max_length=200)
    bik = models.CharField(max_length=200)
    inn = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    fax = models.CharField(max_length=200)
    email = models.EmailField()
    operation_mode = models.TextField()
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

class Region(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class DegreeOfImprovementsDwelling(models.Model):
    """степень благоустройства жилого помещения"""
    name = models.CharField(max_length=500)
    def __str__(self):
        return self.name

class NormValidity(models.Model):
    """ Период действия норматива
    start - дата, с которой начинает действовать норматив
    end - дата окончания действия норматива
    """
    start = models.DateField()
    end = models.DateField()
    def __str__(self):
        return "%s->%s" % (str(self.start), str(self.end))

class ColdWaterNorm(models.Model):
    """ Нормаив по холодному водоснабжению.
    region - ссылка на регион
    degree_of_improvements - ссылка на степень благоустроенности жилого помещения
    validity - ссылка на период действия норматива
    norm - норматив
    """
    region = models.ForeignKey(Region)
    degree_of_improvements = models.ForeignKey(DegreeOfImprovementsDwelling)
    validity = models.ForeignKey(NormValidity)
    norm = models.FloatField()

class ResourceSupplyOrganization(models.Model):
    """Ресурсно-снабжающая организация
    TODO: Добавить ссылку на населенный пункт.
    """
    name = models.CharField(max_length=200)
    OGRN = models.CharField(max_length=20)
    INN = models.CharField(max_length=20)

class TariffType(models.Model):
    """Тип тарифа: Население либо бюджетные организации"""
    BUDGETARY_CONSUMERS = 'BUDGETARY_CONSUMERS'
    POPULATION = 'POPULATION'
    TARIFF_TYPES = (
        (BUDGETARY_CONSUMERS, 'Бюджетные потребители'),
        (POPULATION, 'Население'),
    )

class TariffValidity(models.Model):
    """ Период действия тарифа
    start - дата, с которой начинает действовать тариф
    end - дата окончания действия тарифа
    """
    start = models.DateField()
    end = models.DateField()

class ColdWaterTariff(models.Model):
    """Тариф по услуге холодного водоснабжения для конкретного клиента."""
    type = models.ForeignKey(TariffType)
    resource_supply_org = models.ForeignKey(ResourceSupplyOrganization)
    validity = models.ForeignKey(TariffValidity)
    value = models.FloatField()
    
class HeatingTariff(models.Model):
    """Тариф по услуге холодного водоснабжения для конкретного клиента."""
    type = models.ForeignKey(TariffType)
    resource_supply_org = models.ForeignKey(ResourceSupplyOrganization)
    validity = models.ForeignKey(TariffValidity)
    value = models.FloatField()

class RealEstate(models.Model):
    """Объект недвижимости.

    Объектом недвижимости может являться многоквартирный дом, жилой дом,
    квартира, комната. При этом у модели есть связь, которая показывает,
    например, какая именно комната принадлежит какой именно квартире.

    cold_water_counter_setup_date -- это дата установки счетчика холодной
    воды. Не совсем понятна ситуация со сменой счетчиков, т.е. должна ли
    находится информация cold_water_counter_setup_date именно в объекте
    недвижимости.

    TODO: со временем перенести поля residential residents в отдельную
    таблицу, потому что эта информация может меняться, а иногда полезно делать
    перерасчет, но информация, возможна будет потеряна.
    residential -- флаг, указывающий жилое ли помещение. Находится здесь,
    потому что как используется помещение зависит больше от клиента, а не от
    помещения.
    residents - количество зарегестированных (проживающих)
    space_of_joint_estate - Площадь совместного имущества (Площади межквартирных лестничных площадок, лестниц, коридоров, тамбуров, холлов, вестибюлей, колясочных, помещений охраны (консьержа) в этом многоквартирном доме, не принадлежащих отдельным собственникам
    degree_of_improvements - Степень благоустройтва жилого помещения (Ссылка).

    """
    FLAT_TYPE = 'f'
    ROOM_TYPE = 'r'
    HOUSE_TYPE = 'h'
    BUILDING_TYPE = 'b'
    SHARE_TYPE = 's'
    REAL_ESTATE_TYPES = (
        (FLAT_TYPE, 'Квартира'),
        (ROOM_TYPE, 'Комната'),
        (HOUSE_TYPE, 'Дом'),
        (BUILDING_TYPE, 'Здание'),
        (SHARE_TYPE, 'Общий блок'),
    )

    address = models.CharField(max_length=200)
    region = models.ForeignKey(Region)
    parent = models.ForeignKey('self', null=True, blank=True, default = None)
    cold_water_counter_setup_date = models.DateField(blank=True, null=True)
    heating_counter_setup_date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=1, choices=REAL_ESTATE_TYPES, default=HOUSE_TYPE)
    space = models.FloatField()
    space_of_joint_estate = models.FloatField()
    residential = models.BooleanField(default=True)
    residents = models.IntegerField(default=-1)
    organization = models.ForeignKey(Organization)
    
    degree_of_improvements = models.ForeignKey(DegreeOfImprovementsDwelling)
    resource_supply_organization = models.ForeignKey(ResourceSupplyOrganization, null=True, blank=True, default = None)
    
    floor_amount = models.IntegerField(blank=True, null=True)
    commissioning_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.address
    def get_absolute_url(self):
        return reverse('accounting:update_real_estate', kwargs={'pk': self.pk})

class Account(models.Model):
    real_estate = models.ForeignKey(RealEstate)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    owners = models.TextField()
    def __str__(self):
        return "(%s: %s {%.2f})" % (str(self.real_estate), self.owners, self.balance)

class Payment(models.Model):
    """Платеж.

    Платеж увеличивает сумму на лицевом счете клиента.
    """
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    balance_before_payment = models.DecimalField(max_digits=8, decimal_places=2)
    account = models.ForeignKey(Account)
    date = models.DateField()
    comment = models.TextField(null=True, blank=True, default = None)

class ServiceClient(models.Model):
    """Связь услуга-клиент.

    Связь указывает на то, какая именно услуга потребляется определенным
    клиентом. Альтернатива выставить флаг в модели Client, но тогда не сможем
    отключать услугу, выставлять ее время.
    """
    COLD_WATER_SERVICE = 'COLD_WATER_SERVICE'
    HOT_WATER_SERVICE = 'HOT_WATER_SERVICE'
    HEATING_SERVICE = 'HEATING_SERVICE'
    SERVICE_NAMES = (
        (COLD_WATER_SERVICE, 'Холодное водоснабжение'),
        (HOT_WATER_SERVICE, 'Горячее водоснабжение'),
        (HEATING_SERVICE, 'Отопление'),
    )
    real_estate = models.ForeignKey(RealEstate)
    service_name = models.CharField(max_length=100, choices=SERVICE_NAMES, default=COLD_WATER_SERVICE)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    def __str__(self):
        return "#%s(%s->%s)" % (self.service_name, str(self.start), str(self.end))

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

class ColdWaterVolumeODN(models.Model):
    """Вычисления объема потребления холодной для помещения на ОДН."""
    period = models.ForeignKey(Period)
    volume = models.FloatField()
    real_estate = models.ForeignKey(RealEstate)
    date = models.DateField()
    def __str__(self):
        return str(self.date)

class ColdWaterNormODN(models.Model):
    """Норматив потребления холодного водоснабжения на ОДН."""
    region = models.ForeignKey(Region)
    validity = models.ForeignKey(NormValidity)
    norm = models.FloatField()
    
class DirectionUsing(models.Model):
    """Направление использования"""
    name = models.CharField(max_length=200)

class DirectionUsingNorm(models.Model):
    """TODO: Необходимо добавить регион (ссылку на субъект РФ)"""
    direction_using = models.ForeignKey(DirectionUsing)
    validity = models.ForeignKey(NormValidity)
    value = models.FloatField()
    def __str__(self):
        return "%s %f с %s по %s" % (self.direction_using.name, self.value, self.validity.start, str(self.validity.end))

class LandPlotAndOutbuilding(models.Model):
    """Земельный участок и надворные постройки
    count - количество единиц направлений использования"""
    count = models.IntegerField()
    real_estate = models.ForeignKey(RealEstate)
    direction_using_norm = models.ForeignKey(DirectionUsingNorm)

class HeatingReading(models.Model):
    """Показания приборов учета отопления"""
    period = models.ForeignKey(Period)
    value = models.FloatField()
    real_estate = models.ForeignKey(RealEstate)
    date = models.DateField()
    def __str__(self):
        return "%s: %s" % (str(self.period), str(self.value))

class HeatingVolume(models.Model):
    """Вычисления объема потребления услуги по отоплению"""
    period = models.ForeignKey(Period)
    volume = models.FloatField()
    real_estate = models.ForeignKey(RealEstate)
    date = models.DateField()
    def __str__(self):
        return str(self.date)

class HeatingVolumeODN(models.Model):
    """Вычисления объема потребления услуги по отоплению на ОДН."""
    period = models.ForeignKey(Period)
    volume = models.FloatField()
    real_estate = models.ForeignKey(RealEstate)
    date = models.DateField()
    def __str__(self):
        return str(self.date)

class HeatingNorm(models.Model):
    """Норматив потребления услуги по отоплению.
    commissioning_type - Тип ввода в эксплуатацию. Используется 2 типа: до 2000 года и начиная с 2000 года.
    floor_amount - Максимальное количество этажей - 9
    """

    COMMISIONING_BEFORE = 'COMMISIONING_BEFORE'
    COMMISIONING_AFTER = 'COMMISIONING_AFTER'
    COMMISIONING_TYPES = (
        (COMMISIONING_BEFORE, 'Здание введено в эксплуатацию до 1999 года включительно'),
        (COMMISIONING_AFTER, 'Здание введено в эксплуатацию начиная с 2000 года'),
    )

    commissioning_type = models.CharField(max_length=100, choices=COMMISIONING_TYPES, default=COMMISIONING_BEFORE)
    region = models.ForeignKey(Region)
    validity = models.ForeignKey(NormValidity)
    floor_amount = models.IntegerField()
    value = models.FloatField()

from django.db import models
from django.contrib.auth.models import User

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
    
    LOCALITY_TYPES = (
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
    type = models.CharField(max_length=1, choices=LOCALITY_TYPES, default=HAMLET)
    subject_rf = models.ForeignKey(SubjectRF)
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

class HouseAddress(models.Model):
    """ Адрес дома. Не хранит номера помещений. Содержит только номера домов.
    """
    #номер дома (входят вся информация о номере дома. Например, "Королёва 40 к48/1" или "Королёва 40 к40а")
    #TODO: Хранить номер квартиры отдельно. Номер квартиры хранить в одном поле. (кв 54 ком 2 или офис 34)
    index = models.CharField(max_length=6)
    street = models.ForeignKey(Street)
    house_number = models.CharField(max_length=10)
    def __str__(self):
        return "%s, %s" % (self.street.name, self.house_number)

class CommunalService(models.Model):
    """ Коммунальные услуги """
    COLD_WATER = "1"
    HOT_WATER = "2"
    WATER_DISPOSAL = "3"
    HEATING = "4"
    COMMUNAL_RESOURCES = (
        (COLD_WATER, 'Холодное водоснабжение'),
        (HOT_WATER, 'Горячее водоснабжение'),
        (WATER_DISPOSAL, 'Водоотведение'),
        (HEATING, 'Отопление'),
    )
    name = models.CharField(max_length=1, choices=COMMUNAL_RESOURCES, default=COLD_WATER)
    def __str__(self):
        return self.get_name_display()

class WaterNormDescription(models.Model):
    """Описание названий видов нормативов для водоснабжения (холодная, горячая, водоотведение)"""
    
    DEGREE_OF_IMPROVEMENT_DWELLING = '1'
    COMMON_PROPERTY = '2'
    AGRICULTURAL_ANIMALS = '3'
    DIRECTION_USING = '4'
    
    AREA_APPLICATION_TYPES = (
        (DEGREE_OF_IMPROVEMENT_DWELLING, 'Степень благоустройства жилых помещений'),
        (COMMON_PROPERTY, 'Общее имущество'),
        (AGRICULTURAL_ANIMALS, 'Виды сельскохозяйственных животных'),
        (DIRECTION_USING, 'Направления использования'),
    )
    
    description = models.TextField()
    direction_type = models.CharField(max_length=1, choices=AREA_APPLICATION_TYPES, default=DEGREE_OF_IMPROVEMENT_DWELLING)
    
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
    """ Норматив по холодному, горячему водоснабжению и водоотведению.
    type - тип (холодное водоснабжение | горячее водоснабжение | водоотведение)
    value - норматив
    """
    subject_rf = models.ForeignKey(SubjectRF)
    norm_description = models.ForeignKey(WaterNormDescription)
    validity = models.ForeignKey(WaterNormValidity)
    service = models.ForeignKey(CommunalService)
    value = models.FloatField()

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

class HeatingNorm(models.Model):
    """Норматив по отоплению.
    commissioning_type - Тип ввода в эксплуатацию. Используется 2 типа: до 2000 года и начиная с 2000 года.
    floor_amount - количество этажей
    """

    COMMISIONING_TO_1999 = '1'
    COMMISIONING_FROM_2000 = '2'
    COMMISIONING_TYPES = (
        (COMMISIONING_TO_1999, 'Введено в эксплуатацию до 1999 года включительно'),
        (COMMISIONING_FROM_2000, 'Введено в эксплуатацию после 1999'),
    )

    municipal_area = models.ForeignKey(MunicipalArea)
    validity = models.ForeignKey(HeatingNormValidity)
    commissioning_type = models.CharField(max_length=1, choices=COMMISIONING_TYPES, default=COMMISIONING_TO_1999)
    floor_amount = models.IntegerField()
    value = models.FloatField()

    def __str__(self):
        return "[%s, Количество этажей: %d]\tНорматив: %f" % (self.get_commissioning_type_display(), self.floor_amount, self.value)
"""\Данные для норматива по отоплению"""

class RealEstate(models.Model):
    """Объект недвижимости.

    Объектом недвижимости может являться многоквартирный дом, жилой дом,
    квартира, комната. При этом у модели есть связь, которая показывает,
    например, какая именно комната принадлежит какой именно квартире.

    TODO: со временем перенести поля residential residents в отдельную
    таблицу, потому что эта информация может меняться, а иногда полезно делать
    перерасчет, но информация, возможна будет потеряна.
    residential -- флаг, указывающий жилое ли помещение. Находится здесь,
    потому что как используется помещение зависит больше от клиента, а не от
    помещения.
    residents - количество зарегестированных (проживающих)

    """
    MULTIPLE_DWELLING = "1"
    FLAT = "2"
    ROOM = "3"
    HOUSE = "4"
    MUNICIPAL_OBJECT = "5"
    BUILDING = "6"
    
    BUILDING_TYPES = (
        (MULTIPLE_DWELLING, 'Многоквартирный дом'),
        (FLAT, 'Квартира'),
        (ROOM, 'Комната'),
        (HOUSE, 'Частный дом'),
        (MUNICIPAL_OBJECT, 'Муниципальное здание'),
        (BUILDING, 'Здание'),
    )
    type = models.CharField(max_length=1, choices=BUILDING_TYPES, default=HOUSE)
    address = models.ForeignKey(HouseAddress)
    number = models.CharField (max_length=10, blank=True, default = None) # Номер помещения (Для parent самого верхнего уровня это поле пустое)
    parent = models.ForeignKey('self', null=True, blank=True, default = None)
    residential = models.BooleanField(default=True)

    def __str__(self):
        return "%s, %s, %s, %s %s" % (self.address.street.locality.name, self.address.street.name, self.address.house_number, self.get_type_display(), self.number)

"""
class OrganizationClient(models.Model):
    \"""Связь Клиент(Объект недвижимость) - Организация. Один объект недвижимости может быть клиентом нескольких организаций.\"""
    organization = models.ForeignKey(Organization)
    real_estate = models.ForeignKey(RealEstate)
"""

class ClientService(models.Model):
    """Связь услуга-клиент.

    Связь указывает на то, какая именно услуга потребляется определенным
    клиентом (объектом недвижимости).
    """
    real_estate = models.ForeignKey(RealEstate)
    service = models.ForeignKey(CommunalService)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)

class TechnicalPassport(models.Model):
    """ Технический паспорт помещения."""
    real_estate = models.ForeignKey(RealEstate)
    floor_amount = models.IntegerField(default=1) # Количество этажей
    commissioning_date = models.DateField() # Ввод здания в эксплуатацию
    space = models.FloatField()

class RealEstateOwner(models.Model):
    """ Связь Недвижимость - собственник"""
    real_estate = models.ForeignKey(RealEstate)
    owner = models.CharField(max_length=30) #MayBe: Перенести в отдельную таблицу и использовать ссылку на 'owner'
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.owner

class HomeownershipHistory(models.Model):
    """История домовладения.
    count - количество единиц направлений использования"""
    #TODO: Есть ли смысл хранить в этой таблице зависимость "Количество проживающих/зарегестированных" к "помещению (абоненту)"
    real_estate = models.ForeignKey(RealEstate)
    water_description = models.ForeignKey(WaterNormDescription)
    count = models.FloatField()
    start = models.DateField()

class Organization(models.Model):
    """Организация.

    МУП - это частный случай организации, поэтому МУП находится в этой модели.
    Организационно-правовая форма (AO, OAO, ЗАО, ООО, МУП)
    Реквизиты организации:
    - Полное наименование
    - ИНН
    - КПП
    - ОГРН
    - Юр адрес
    - Физ адрес
    - Почтовый адрес
    Банковские реквизиты:
    - Наименование банка
    - БИК
    - Корреспондентский счет
    - Расчетный счет
    """
    # Организационно-правовая форма
    AO  = 'АО'
    MUP = 'МУП'
    OAO = 'ОАО'
    OOO = 'ООО'
    PAO = 'ПАО'
    ZAO = 'ЗАО'
    LEGAL_FORMS = (
        (AO, 'Акционерное общество'),
        (MUP, 'Муниципальное унитарное предприятие'),
        (OAO, 'Открытое акционерное общество'),
        (OOO, 'Общество с ограниченной ответственностью'),
        (PAO, 'Публичное акционерное общество'),
        (ZAO, 'Закрытое акционерное общество'),
    )   
    legal_form = models.CharField(max_length=3, choices=LEGAL_FORMS, default=MUP)
    
    # Название организации (полное\сокращенное)
    short_name = models.CharField(max_length=100) #TODO: Нужно ли это поле?
    full_name = models.TextField()
    
    # Реквизиты организации
    taxpayer_identification_number = models.CharField(max_length=25) # ИНН (TIN)
    tax_registration_reason_code = models.CharField(max_length=25) # КПП
    primary_state_registration_number = models.CharField(max_length=25) # ОГРН (PSRN)
    
    #Банковские реквизиты
    bank_identifier_code = models.CharField(max_length=25) # БИК (BIC)
    corresponding_account = models.CharField(max_length=25) # Корреспондентский счет
    operating_account = models.CharField(max_length=25) # Расчетный счет
    
    # vat - Налог на добавленную стоимость. Отлата НДС
    #TODO: Возможна ли сутация, когда для одной организации для разных услуг используется разное значение этого поля? В этом случае перенести поле в 'Tariff' 
    vat_payment = models.BooleanField(default=False)
        
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.CharField(max_length=20)
    operating_mode=models.TextField()
    
    address = models.ForeignKey(HouseAddress)

    # Услуги организации
    services = models.ManyToManyField(CommunalService)
    # Абоненты организации
    abonents = models.ManyToManyField(RealEstate)
    
    def __str__(self):
        return '%s "%s"' % (self.legal_form, self.full_name)

"""Таблицы, хранящие информацию о тарифах"""
class TariffValidity(models.Model):
    """ Период действия тарифа
    Для отопления и воды одинаковые периоды
    start - дата, с которой начинает действовать тариф
    end - дата окончания действия тарифа
    """
    start = models.DateField()
    end = models.DateField()

class Tariff(models.Model):
    """Тариф для соответствующей услуги"""
    BUDGETARY_CONSUMERS = '1'
    POPULATION = '2'
    TARIFF_TYPES = (
        (BUDGETARY_CONSUMERS, 'Бюджетные потребители'),
        (POPULATION, 'Население'),
    )

    service = models.ForeignKey(CommunalService)
    organization = models.ForeignKey(Organization)
    validity = models.ForeignKey(TariffValidity)
    type = models.CharField(max_length=1, choices=TARIFF_TYPES, default=POPULATION)
    value = models.FloatField()

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
        return "%s" % (str(self.end.strftime("%B %Y")))

class CalculationService(models.Model):
    """ Вычисления объема потребления и размер платы за определенную услугу. 
    volume - абсолютное значение (если индивидуальное потребление, то это суммарный объем)"""
    INDIVIDUAL = "1"
    COMMON_PROPERTY = "2"
    CONSUMPTION_TYPES = (
        (INDIVIDUAL, 'Индивидуальное потребление'),
        (COMMON_PROPERTY, 'Общедомовые нужны'),
    )
    
    real_estate = models.ForeignKey(RealEstate)
    communal_service = models.ForeignKey(CommunalService)
    consumption_type = models.CharField(max_length=1, choices=CONSUMPTION_TYPES, default=INDIVIDUAL)
    period = models.ForeignKey(Period)
    volume = models.FloatField()
    amount = models.FloatField()
    def __str__(self):
        return "re_id=%d, name='%s', consumption_type='%s', preriod_id=%d" % (self.real_estate.id, self.communal_service.get_name_display(), self.get_consumption_type_display(), self.period.id)

class AccountOperation(models.Model):
    """ Лицевой счет """
    WRITE_OFF = "1"
    TOP_UP = "2"
    OPERATION_TYPES = (
        (WRITE_OFF, 'Списание'),
        (TOP_UP, 'Зачисление'),
    )
    
    real_estate = models.ForeignKey(RealEstate)
    balance = models.FloatField()
    operation_type = models.CharField(max_length=1, choices=OPERATION_TYPES, default=WRITE_OFF)
    operation_date = models.DateField()
    amount = models.FloatField()
    def __str__(self):
        return "%d %f %s %f" % (self.real_estate.id, self.balance, self.operation_type, self.amount)

class UserOrganization(models.Model):
    """Связь пользователь-организация.
    Пользователи бывают администраторами, клиентами организации, работниками
    организации. Связь показывает какой именно пользователь сайта является
    работником организации.
    """
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization, null=True, blank=True, default = None)

class Counter(models.Model):
    """
    Таблица содержит информацию об установленных счетчиках.
    Хранит информацию обо всех счетчиках.
    Счетчик может выйти из строя и быть заменен, поэтому для одного и того же типа счетчика может быть несколько записей для объекта недвижимости.
    """
    CUM = '1'
    GCAL = '2'
    JOULE = '3'
    WATT = '4'
    UNIT_TYPES = (
        (CUM, 'м3'),
        (GCAL, 'ГКал'),
        (JOULE, 'Дж'),
        (WATT, 'Вт'),
    )
    number = models.CharField(max_length=20)
    service = models.ForeignKey(CommunalService)
    real_estate = models.ForeignKey(RealEstate)
    unit_type = models.CharField(max_length=1, choices=UNIT_TYPES, default=CUM)
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    def __str__(self):
        readings = CounterReading.objects.filter(counter=self)
        last_reading = readings.last().value if len(readings) > 0 else -1
        return "%s (%f)" % (self.service.get_name_display(), last_reading)

class CounterReading(models.Model):
    """
    Показания всех приборов учета.
    Так как информация по показаниям однотипная, вся информация будет храниться в одной таблице.
    В одном периоде может быть несколько показаний.
     MayBe: Нужно ли хранить здесь поле 'period'? Период можно получить по 'date'
    """
    counter = models.ForeignKey(Counter)
    date = models.DateField()
    period = models.ForeignKey(Period)
    value = models.DecimalField(max_digits=9, decimal_places=3)

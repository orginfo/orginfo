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
    street = models.ForeignKey(Street)
    house_number = models.CharField(max_length=10)
    def __str__(self):
        return "%s, %s" % (self.street.name, self.house_number)

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


class Service(models.Model):
    """ Хранит все сервисы, предоставляемые организациями. Так же включает ОДН"""
    #TODO: или это должна быть отдельная структура?
     
    COLD_WATER = '1'
    HOT_WATER = '2'
    WATER_DISPOSAL = '3'
    SERVICE_WATER = '4'
    HEATING = '5'
    SERVICES = (
        (COLD_WATER, 'Холодное водоснабжение'),
        (HOT_WATER, 'Горячее водоснабжение'),
        (WATER_DISPOSAL, 'Водоотведение'),
        (SERVICE_WATER, 'Техническая вода'),
        (HEATING, 'Тепловая энергия'),
    )
    service = models.CharField(max_length=1, choices=SERVICES, default=COLD_WATER)
    def __str__(self):
        return self.get_service_display()

class LegalForm(models.Model):
    """Организационно-правовая форма (AO, OAO, ЗАО, ООО, МУП)"""
    #MayBe: Перенести в 'Organization'.
    short_name = models.CharField(max_length=5)
    full_name = models.CharField(max_length=50)

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
    # Тип организации:
    RESOURCE_SUPPLY = 1
    BANK = 2
    TYPES = (
        (RESOURCE_SUPPLY, 'Холодное водоснабжение'),
        (BANK, 'Горячее водоснабжение'),
    )
    type = models.CharField(max_length=1, choices=TYPES, default=RESOURCE_SUPPLY)
    
    # Организационно-правовая форма
    AO  = 'АО'
    MUP = 'МУП'
    OOO = 'ООО'
    PAO = 'ПАО'
    ZAO = 'ЗАО'
    LEGAL_FORMS = (
        (AO, 'Акционерное общество'),
        (MUP, 'Муниципальное унитарное предприятие'),
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
    bank = models.ForeignKey('self', null=True, blank=True, default = None)
    bank_identifier_code = models.CharField(max_length=25) # БИК (BIC)
    corresponding_account = models.CharField(max_length=25) # Корреспондентский счет
    operating_account = models.CharField(max_length=25) # Расчетный счет
    
    # vat - Налог на добавленную стоимость. Отлата НДС
    #TODO: Возможна ли сутация, когда для одной организации для разных услуг используется разное значение этого поля? В этом случае перенести поле в 'Tariff' 
    vat_payment = models.BooleanField(default=False)
        
    phone = models.CharField(max_length=30)
    fax = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name

"""Данные по тарифам для воды"""
class WaterTariffValidity(models.Model):
    start = models.DateField()
    end = models.DateField()
    def __str__(self):
        return "%s->%s" % (str(self.start), str(self.end))
"""\Данные по тарифам для воды"""

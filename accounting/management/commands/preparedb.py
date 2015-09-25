from django.core.management.base import BaseCommand
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality
from accounting.models import Street, HouseAddress
from accounting.models import RealEstate, HomeownershipHistory, RealEstateOwner, TechnicalPassport
from accounting.models import WaterNormDescription, WaterNormValidity, WaterNorm, TariffValidity, Tariff
from accounting.models import HeatingNormValidity, HeatingNorm
from accounting.models import Organization, CommunalService, ClientService
from accounting.models import Period, CalculationService, AccountOperation, Counter, CounterReading, Account
import os.path
from orginfo.settings import BASE_DIR
from datetime import datetime
import pytz

def fill_total_info():
    HouseAddress.objects.all().delete()
    RealEstate.objects.all().delete()
    RealEstateOwner.objects.all().delete()
    TechnicalPassport.objects.all().delete()
    HomeownershipHistory.objects.all().delete()
    
    #Услуги
    srv1 = CommunalService.objects.get(name=CommunalService.COLD_WATER)
    srv2 = CommunalService.objects.get(name=CommunalService.HEATING)
    
    # Адрес для КК
    loc_kk = Locality.objects.get(name="Кудельный Ключ") 
    street_kk = Street.objects.get(locality=loc_kk, name="Центральная")
    address_kk = HouseAddress(index="633447", street=street_kk, house_number="6")
    address_kk.save()
    
    # Организации
    # Добавление КК
    Organization.objects.all().delete()
    kluchevscoe = Organization(short_name="Ключевское", full_name="Ключевское",
                               taxpayer_identification_number="5438113504",
                               tax_registration_reason_code="543801001",
                               primary_state_registration_number="10454045761",
                               bank_identifier_code="045004850",
                               corresponding_account="30101810100000000850",
                               operating_account="40702810609240000158",
                               phone="8(38340)31-104, 8(38340)31-238",
                               email="kluchinat@mail.ru",
                               operating_mode="Режим работы: Пн.-Пт. 8.00-17.00, Обед: 13.00-14.00",
                               address=address_kk)
    kluchevscoe.save()
    # Добавление услуг в КК
    kluchevscoe.services.add (srv1)
    kluchevscoe.services.add (srv2)
    kluchevscoe.save()
    
    # Заполнение данных для Кудельно-Ключевской
    path = os.path.join(BASE_DIR, "data", "preparedb", "Total_KK.txt")
    water_norm_validity = WaterNormValidity.objects.get(start ='2013-12-01', end='2015-03-31')
    fill_total_kk(water_norm_validity, path, kluchevscoe)
    
    
    # Заполнение МУП "Нечаевское"
    # Адрес 
    loc_n = Locality.objects.get(name="Нечаевский") 
    street_n = Street.objects.get(locality=loc_n, name="Весенняя")
    address_n = HouseAddress(index="633422", street=street_n, house_number="11")
    address_n.save()
    
    neсhaevscoe = Organization(short_name="Нечаевское", full_name="Нечаевское",
                              taxpayer_identification_number="5438315941",
                              tax_registration_reason_code="543801001",
                              primary_state_registration_number="1055461017248",
                              bank_identifier_code="045004784",
                              corresponding_account="30101810700000000784",
                              operating_account="40702810525170000045",
                              phone="8(38340)32-413",
                              fax="8(38340)32-242",
                              email="mupnechaevskoe@yandex.ru",
                              operating_mode="Режим работы: Пн-Чт. 9:00-17:00, Пт. 9:00-16:00, Обед: 13:00-14:00",
                              address=address_n)
    
    neсhaevscoe.save()
    neсhaevscoe.services.add (srv1)
    neсhaevscoe.services.add (srv2)
    neсhaevscoe.save()
    
    # Нечаевский
    path = os.path.join(BASE_DIR, "data", "preparedb", "Total_N.txt")
    water_norm_validity = WaterNormValidity.objects.get(start ='2015-7-01', end='2015-12-31')
    fill_total_kk(water_norm_validity, path, neсhaevscoe)
    
    # Срок действия тарифа по воде
    TariffValidity.objects.all().delete()
    tariff_val1 = TariffValidity(start='2015-01-01', end='2015-06-30')
    tariff_val1.save()
    tariff_val2 = TariffValidity(start='2015-07-01', end='2015-12-31')
    tariff_val2.save()

    # Тарифы организаций
    # КК
    Tariff.objects.all().delete()
    cold_water_tariff = Tariff(service=srv1, organization=kluchevscoe, validity=tariff_val1, value=26.02)
    cold_water_tariff.save()
    cold_water_tariff = Tariff(service=srv1, organization=kluchevscoe, validity=tariff_val1, type=Tariff.BUDGETARY_CONSUMERS, value=26.02)
    cold_water_tariff.save()
    
    cold_water_tariff = Tariff(service=srv1, organization=kluchevscoe, validity=tariff_val2, value=27.12)
    cold_water_tariff.save()
    cold_water_tariff = Tariff(service=srv1, organization=kluchevscoe, validity=tariff_val2, type=Tariff.BUDGETARY_CONSUMERS, value=27.12)
    cold_water_tariff.save()
    
    # Нечаевский
    cold_water_tariff = Tariff(service=srv1, organization=neсhaevscoe, validity=tariff_val1, value=14.74)
    cold_water_tariff.save()
    cold_water_tariff = Tariff(service=srv1, organization=neсhaevscoe, validity=tariff_val1, type=Tariff.BUDGETARY_CONSUMERS, value=14.74)
    cold_water_tariff.save()
    
    cold_water_tariff = Tariff(service=srv1, organization=neсhaevscoe, validity=tariff_val2, value=15.77)
    cold_water_tariff.save()
    cold_water_tariff = Tariff(service=srv1, organization=neсhaevscoe, validity=tariff_val2, type=Tariff.BUDGETARY_CONSUMERS, value=15.77)
    cold_water_tariff.save()

def fill_total_kk(water_norm_validity, path, organization):
    
    start_calc_date = '2015-7-26'
    novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
    history_updated = novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
    account_number = 1
    
    protocol_kk_path = os.path.join(BASE_DIR, "data", "preparedb", "Protocol_KK.txt")
    err_file = open(protocol_kk_path, 'w', encoding='utf-8')
    
    file = open(path, 'r', encoding='utf-8')
    for line in file:
        index = 0
        
        locality_name = ""  # 0
        street_name = ""    # 1
        house_nr = ""       # 2
        number = ""         # 3
        owner = ""          # 4
        space = ""          # 5
        norm = ""           # 6
        residents = ""      # 7
        debts1 = "" # 8
        debts2 = "" # 9
        water_srv = ""      # 10
        p15 = ""    # 11
        p16 = ""    # 12
        p17 = ""    # 13
        p18 = ""    # 14
        p19 = ""    # 15
        p20 = ""    # 16
        p21 = ""    # 17
        p22 = ""    # 18
        p23 = ""    # 19
        p24 = ""    # 20
        p25 = ""    # 21
        p26 = ""    # 22
        p27 = ""    # 23
        p28 = ""    # 24
        p29 = ""    # 25
        p30 = ""    # 26
        p31 = ""    # 27
        for part in line.split("\t"):
            part = part.strip().replace(u'\ufeff', '')
            if part == "\n":
                continue
            
            if index == 0:
                locality_name = part
            elif index == 1:
                street_name = part
            elif index == 2:
                house_nr = part
            elif index == 3:
                number = part
            elif index == 4:
                owner = part
            elif index == 5:
                space = part
            elif index == 6:
                norm = part
            elif index == 7:
                residents = part
            elif index == 8:
                debts1 = part
            elif index == 9:
                debts2 = part
            elif index == 10:
                water_srv = part
            elif index == 11:
                p15 = part
            elif index == 12:
                p16 = part
            elif index == 13:
                p17 = part
            elif index == 14:
                p18 = part
            elif index == 15:
                p19 = part
            elif index == 16:
                p20 = part
            elif index == 17:
                p21 = part
            elif index == 18:
                p22 = part
            elif index == 19:
                p23 = part
            elif index == 20:
                p24 = part
            elif index == 21:
                p25 = part
            elif index == 22:
                p26 = part
            elif index == 23:
                p27 = part
            elif index == 24:
                p28 = part
            elif index == 25:
                p29 = part
            elif index == 26:
                p30 = part
            elif index == 27:
                p31 = part
            else:
                pass
            index = index + 1

        if len(locality_name) == 0:
            continue
        
        loc = Locality.objects.get(name=locality_name)
        if len(street_name) == 0:
            continue
        street = Street.objects.get(locality=loc, name=street_name)
        
        if len(house_nr) == 0:
            continue
        address = None
        if HouseAddress.objects.filter(street=street, house_number=house_nr).exists():
            address = HouseAddress.objects.get(street=street, house_number=house_nr)
        else:
            postal_code = ""
            if loc.name == "Боровлянка":
                postal_code = "633446"
            elif loc.name == "Зверобойка":
                postal_code = "633447"
            elif loc.name == "Кудельный Ключ":
                postal_code = "633447"
            elif loc.name == "Прямушка":
                postal_code = "633447"
            elif loc.name == "Шубкино":
                postal_code = "633447"
            elif loc.name == "Нечаевский":
                postal_code = "633422"
            
            address = HouseAddress(index=postal_code, street=street, house_number=house_nr)
            address.save()
        
        real_estate = None
        if RealEstate.objects.filter(address=address, number="").exists():
            real_estate = RealEstate.objects.get(address=address, number="")
        else:
            real_estate = RealEstate(address=address, number="")
            real_estate.save()

        if len(number) != 0:
            if RealEstate.objects.filter(address=address, number=number).exists():
                exist_obj = RealEstate.objects.get(address=address, number=number)
                err_desc = str(exist_obj) + ' was exists\n'
                err_file.write(str(err_desc))
                continue
            
            #RealEstate.objects.filter(address=address, number="").update(type=RealEstate.MULTIPLE_DWELLING)
            real_estate.type = RealEstate.MULTIPLE_DWELLING
            real_estate.save()
            child_real_estate = RealEstate(type=RealEstate.FLAT, address=address, parent=real_estate, number=number)
            child_real_estate.save()
            
            real_estate = child_real_estate 
            
        organization.abonents.add(real_estate)
        
        # Account
        account = Account(real_estate=real_estate, account_number=account_number)
        account.save()
        account_number = account_number + 1
        
        if len(owner) != 0:
            real_estete_owner = RealEstateOwner(real_estate=real_estate, owner=owner, start=start_calc_date)
            real_estete_owner.save()
        
        if len(space) != 0:
            real_estate_space = float(space)
            technical_passport = TechnicalPassport(real_estate=real_estate, commissioning_date='1999-01-01', space=real_estate_space)
            technical_passport.save()
        
        count = 0
        if len(norm) != 0:
            norm_value = float(norm)
            
            water_desc = None
            if norm_value == 6.47 or norm_value == 6.0 or norm_value == 7.764:
                water_desc = WaterNormDescription.objects.get(description='Жилые помещения (в том числе общежития) с холодным водоснабжением, водонагревателями, канализованием, оборудованные ваннами, душами, раковинами, кухонными мойками и унитазами', direction_type=WaterNormDescription.DEGREE_OF_IMPROVEMENT_DWELLING)
            else:
                service = CommunalService.objects.get(name=CommunalService.COLD_WATER)
                water_norm = WaterNorm.objects.get(validity=water_norm_validity, service=service, value=norm_value)
                water_desc = water_norm.norm_description
                
        if len(residents) != 0:
            count = int(residents)
        
        if len(norm) != 0 and len(residents) != 0:
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        # AccountOperation
        balance = 0.0
        if len(debts1) != 0:
            balance = balance + float(debts1)
        
        if len(debts2) != 0:
            balance = balance + float(debts2)
        
        if len(debts1) != 0 or len(debts2) != 0:
            operation = AccountOperation(real_estate=real_estate, balance=balance, operation_type=AccountOperation.WRITE_OFF, operation_date=start_calc_date, amount=0.0)
            operation.save()
        else:
            err_desc = str(real_estate) + ' - not balance\n'
            err_file.write(str(err_desc))
        
        if len(water_srv) != 0:
            continue
        service = CommunalService.objects.get(name=CommunalService.COLD_WATER)
        client_srv = ClientService(real_estate=real_estate, service=service, start=start_calc_date)
        client_srv.save()
        
        if len(p15) != 0:
            count = int(p15)
            water_desc = WaterNormDescription.objects.get(description="Крупный рогатый скот", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p16) != 0:
            count = int(p16)
            water_desc = WaterNormDescription.objects.get(description="Крупный рогатый скот, молодняк", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p17) != 0:
            count = int(p17)
            water_desc = WaterNormDescription.objects.get(description="Лошади", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p18) != 0:
            count = int(p18)
            water_desc = WaterNormDescription.objects.get(description="Свиньи", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p19) != 0:
            count = int(p19)
            water_desc = WaterNormDescription.objects.get(description="Овцы", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p20) != 0:
            count = int(p20)
            water_desc = WaterNormDescription.objects.get(description="Козы", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p21) != 0:
            count = int(p21)
            water_desc = WaterNormDescription.objects.get(description="Куры, индейки", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p22) != 0:
            count = int(p22)
            water_desc = WaterNormDescription.objects.get(description="Утки, гуси", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p23) != 0:
            count = int(p23)
            water_desc = WaterNormDescription.objects.get(description="Лошади, молодняк", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p24) != 0:
            count = int(p24)
            water_desc = WaterNormDescription.objects.get(description="Свиньи, молодняк", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(residents) != 0:
            count = int(residents)
            
            if len(p25) != 0:
                water_desc = WaterNormDescription.objects.get(description="Баня при наличии водопровода")
                homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
                homeownership_history.save()
            
            if len(p26) != 0:
                water_desc = WaterNormDescription.objects.get(description="Баня при водоснабжении из уличной колонки")
                homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
                homeownership_history.save()
        
        if len(p27) != 0:
            count = int(p27)
            water_desc = WaterNormDescription.objects.get(description="Мойка мотоцикла")
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p28) != 0:
            count = int(p28)
            water_desc = WaterNormDescription.objects.get(description="Мойка автомобиля при наличии водопровода")
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
        
        if len(p29) != 0:
            count = int(p29)
            water_desc = WaterNormDescription.objects.get(description="Мойка автомобиля при водоснабжении из уличной колонки")
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
            
        if len(p30) != 0:
            count = float(p30)
            water_desc = WaterNormDescription.objects.get(description="Полив земельного участка при наличии водопровода")
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
    
        if len(p31) != 0:
            count = float(p31)
            water_desc = WaterNormDescription.objects.get(description="Полив земельного участка при водоснабжении из уличной колонки")
            homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc, count=count, start=start_calc_date, updated=history_updated)
            homeownership_history.save()
    file.close()

def fill_period():
    Period.objects.all().delete()
    period1 = Period(serial_number=1, start='2014-12-26', end='2015-1-25')
    period1.save()
    period2 = Period(serial_number=1, start='2015-1-26', end='2015-2-25')
    period2.save()
    period3 = Period(serial_number=1, start='2015-2-26', end='2015-3-25')
    period3.save()
    period4 = Period(serial_number=1, start='2015-3-26', end='2015-4-25')
    period4.save()
    period5 = Period(serial_number=1, start='2015-4-26', end='2015-5-25')
    period5.save()
    period6 = Period(serial_number=1, start='2015-5-26', end='2015-6-25')
    period6.save()
    period7 = Period(serial_number=1, start='2015-6-26', end='2015-7-25')
    period7.save()
    period8 = Period(serial_number=1, start='2015-7-26', end='2015-8-25')
    period8.save()

def preapare_water_counter():
    Counter.objects.all().delete()
    CounterReading.objects.all().delete()
    
    path = os.path.join(BASE_DIR, "data", "preparedb", "Counter_KK.txt")
    preapare_cold_water_counter(path)
    
    path = os.path.join(BASE_DIR, "data", "preparedb", "Counter_N.txt")
    preapare_cold_water_counter(path)

def preapare_cold_water_counter(path):
    cold_water_service = CommunalService.objects.get(name = CommunalService.COLD_WATER)
    
    file = open(path, 'r', encoding='utf-8')
    for line in file:
        index = 0
        
        locality_name = ""      # 0
        street_name = ""        # 1
        house_nr = ""       # 2
        number = ""         # 3
        counter_number = "" # 4
        start = ""              # 5
        april = ""              # 6
        may = ""                # 7
        june = ""               # 8
        july = ""               # 9
        for part in line.split("\t"):
            part = part.strip().replace(u'\ufeff', '')
            if part == "\n":
                continue
            if index == 0:
                locality_name = part
            elif index == 1:
                street_name = part
            elif index == 2:
                house_nr = part
            elif index == 3:
                number = part
            elif index == 4:
                counter_number = part
            elif index == 5:
                start = part
            elif index == 6:
                april = part
            elif index == 7:
                may = part
            elif index == 8:
                june = part
            elif index == 9:
                july = part
            else:
                pass
            index = index + 1
        
        loc = Locality.objects.get(name=locality_name)
        street = Street.objects.get(locality=loc, name=street_name)
        if HouseAddress.objects.filter(street=street, house_number=house_nr).count() != 1:
            continue
        
        address = HouseAddress.objects.get(street=street, house_number=house_nr)
        if RealEstate.objects.filter(address=address, number=number).count() !=1:
            continue
        real_estate = RealEstate.objects.get(address=address, number=number)
        
        #setup_date = datetime.strptime(start, "%d.%m.%Y")
        setup_date = start
        water_counter = Counter (number=counter_number, service=cold_water_service, real_estate=real_estate, start=setup_date)
        water_counter.save()
        
        if len(april) != 0:
            date_reading = '2015-4-25'
            period = Period.objects.get(start__lte=date_reading, end__gte=date_reading)
            value = float(april)
            reading = CounterReading(counter=water_counter, date=date_reading, period=period, value=value)
            reading.save()
        
        if len(may) != 0:
            date_reading = '2015-5-25'
            period = Period.objects.get(start__lte=date_reading, end__gte=date_reading)
            value = float(may)
            reading = CounterReading(counter=water_counter, date=date_reading, period=period, value=value)
            reading.save()
        
        if len(june) != 0:
            date_reading = '2015-6-25'
            period = Period.objects.get(start__lte=date_reading, end__gte=date_reading)
            value = float(june)
            reading = CounterReading(counter=water_counter, date=date_reading, period=period, value=value)
            reading.save()
        
        if len(july) != 0:
            date_reading = '2015-7-25'
            period = Period.objects.get(start__lte=date_reading, end__gte=date_reading)
            value = float(july)
            reading = CounterReading(counter=water_counter, date=date_reading, period=period, value=value)
            reading.save()

    file.close()

def prepare_db_base():
    # Субъект РФ
    SubjectRF.objects.all().delete()
    subjectRF = SubjectRF(name="Новосибирская область")
    subjectRF.save()

    # Муниципальный район
    MunicipalArea.objects.all().delete()
    municipal_area = MunicipalArea(name="Тогучинский район", subject_rf=subjectRF)
    municipal_area.save()

    # Муниципальное образование
    MunicipalUnion.objects.all().delete()
    union1 = MunicipalUnion(name="Кудельно-Ключевской сельсовет", municipal_area=municipal_area)
    union1.save()
    union2 = MunicipalUnion(name="Нечаевский сельсовет", municipal_area=municipal_area)
    union2.save()

    # Населенный пункт
    Locality.objects.all().delete()
    loc1 = Locality(name="Боровлянка", type=Locality.VILLAGE, subject_rf=subjectRF, municipal_area=municipal_area, municipal_union=union1)
    loc1.save()
    loc2 = Locality(name="Зверобойка", type=Locality.SETTLEMENT, subject_rf=subjectRF, municipal_area=municipal_area, municipal_union=union1)
    loc2.save()
    loc3 = Locality(name="Кудельный Ключ", type=Locality.HAMLET, subject_rf=subjectRF, municipal_area=municipal_area, municipal_union=union1)
    loc3.save()
    loc4 = Locality(name="Прямушка", type=Locality.SETTLEMENT, subject_rf=subjectRF, municipal_area=municipal_area, municipal_union=union1)
    loc4.save()
    loc5 = Locality(name="Шубкино", type=Locality.HAMLET, subject_rf=subjectRF, municipal_area=municipal_area, municipal_union=union1)
    loc5.save()
    loc6 = Locality(name="Нечаевский", type=Locality.SETTLEMENT, subject_rf=subjectRF, municipal_area=municipal_area, municipal_union=union2)
    loc6.save()

    # Улица
    Street.objects.all().delete()
    street1 = Street(name="Центральная", locality=loc1)
    street1.save()
    street2 = Street(name="Новая", locality=loc1)
    street2.save()
    street3 = Street(name="Центральная", locality=loc2)
    street3.save()
    street4 = Street(name="Лесная", locality=loc3)
    street4.save()
    street5 = Street(name="Центральная", locality=loc3)
    street5.save()
    street6 = Street(name="Шубкинская", locality=loc3)
    street6.save()
    street7 = Street(name="Молодежная", locality=loc3)
    street7.save()
    street8 = Street(name="Береговая", locality=loc3)
    street8.save()
    street9 = Street(name="Весенняя", locality=loc3)
    street9.save()
    street10 = Street(name="Новая", locality=loc3)
    street10.save()
    street11 = Street(name="Зеленая", locality=loc3)
    street11.save()
    street12 = Street(name="Заречная", locality=loc3)
    street12.save()
    street13 = Street(name="Центральная", locality=loc4)
    street13.save()
    street14 = Street(name="Центральная", locality=loc5)
    street14.save()
    street15 = Street(name="Школьная", locality=loc5)
    street15.save()
    street16 = Street(name="Зеленая", locality=loc5)
    street16.save()
    street17 = Street(name="Богдана Хмельницкого", locality=loc6)
    street17.save()
    street18 = Street(name="Весенняя", locality=loc6)
    street18.save()
    street19 = Street(name="Поселковая", locality=loc6)
    street19.save()
    street20 = Street(name="Светлая", locality=loc6)
    street20.save()
    street21 = Street(name="Светлый", type=Street.SIDE_STREET, locality=loc6)
    street21.save()
    street22 = Street(name="Совхозная", locality=loc6)
    street22.save()
    street23 = Street(name="Солнечная", locality=loc6)
    street23.save()
    street24 = Street(name="Весенний", type=Street.SIDE_STREET, locality=loc6)
    street24.save()
    
    # ДОКУМЕНТ:
    # ОБ УТВЕРЖДЕНИИ НОРМАТИВОВ ПОТРЕБЛЕНИЯ КОММУНАЛЬНЫХ УСЛУГ ПО ХОЛОДНОМУ ВОДОСНАБЖЕНИЮ, ГОРЯЧЕМУ ВОДОСНАБЖЕНИЮ И ВОДООТВЕДЕНИЮ НА ТЕРРИТОРИИ НОВОСИБИРСКОЙ ОБЛАСТИ
    #
    WaterNormDescription.objects.all().delete()
    # 1. Степень благоустройства жилых помещений
    water_desc1 = WaterNormDescription(description="Жилые помещения (в том числе общежития квартирного типа) с холодным и горячим водоснабжением, канализованием, оборудованные ваннами длиной 1500 - 1700 мм, душами, раковинами, кухонными мойками и унитазами")
    water_desc1.save()
    water_desc2 = WaterNormDescription(description="Жилые помещения (в том числе общежития квартирного типа) с холодным водоснабжением, водонагревателями, канализованием, оборудованные ваннами длиной 1500 - 1700 мм, душами, раковинами, кухонными мойками и унитазами")
    water_desc2.save()
    water_desc3 = WaterNormDescription(description="Жилые помещения (в том числе общежития квартирного типа) с холодным и горячим водоснабжением, канализованием, оборудованные сидячими ваннами длиной 1200 мм, душами, раковинами, кухонными мойками и унитазами")
    water_desc3.save()
    water_desc4 = WaterNormDescription(description="Жилые помещения (в том числе общежития квартирного типа) с холодным водоснабжением, водонагревателями, канализованием, оборудованные сидячими ваннами длиной 1200 мм, душами, раковинами, кухонными мойками и унитазами")
    water_desc4.save()
    water_desc5 = WaterNormDescription(description="Жилые помещения (в том числе общежития квартирного и секционного типа) с холодным и горячим водоснабжением, канализованием, оборудованные душами, раковинами, кухонными мойками и унитазами")
    water_desc5.save()
    water_desc6 = WaterNormDescription(description="Жилые помещения (в том числе общежития) с холодным водоснабжением, водонагревателями, канализованием, оборудованные ваннами, душами, раковинами, кухонными мойками и унитазами")
    water_desc6.save()
    water_desc7 = WaterNormDescription(description="Общежития коридорного типа с холодным и горячим водоснабжением, канализованием, оборудованные душами, раковинами, кухонными мойками и унитазами")
    water_desc7.save()
    water_desc8 = WaterNormDescription(description="Общежития коридорного типа с холодным водоснабжением, водонагревателями, канализованием, оборудованные душами, раковинами, кухонными мойками и унитазами")
    water_desc8.save()
    water_desc9 = WaterNormDescription(description="Жилые помещения (в том числе общежития) с холодным и горячим водоснабжением, канализованием, оборудованные раковинами, кухонными мойками и унитазами")
    water_desc9.save()
    water_desc10 = WaterNormDescription(description="Жилые помещения (в том числе общежития) с холодным водоснабжением, канализованием, оборудованные раковинами, кухонными мойками и унитазами")
    water_desc10.save()
    water_desc11 = WaterNormDescription(description="Жилые помещения (в том числе общежития) с холодным водоснабжением, канализованием, оборудованные раковинами, кухонными мойками")
    water_desc11.save()
    water_desc12 = WaterNormDescription(description="Жилые помещения (в том числе общежития) с холодным водоснабжением (в том числе от уличных колонок), оборудованные кухонными мойками")
    water_desc12.save()
    water_desc13 = WaterNormDescription(description="Жилые помещения (в том числе общежития) с холодным водоснабжением, оборудованные раковинами, кухонными мойками")
    water_desc13.save()

    # 2. Общее имущество
    water_desc14 = WaterNormDescription(description="ОДН", direction_type=WaterNormDescription.COMMON_PROPERTY)
    water_desc14.save()

    # 3. Виды сельскохозяйственных животных
    water_desc15 = WaterNormDescription(description="Крупный рогатый скот", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc15.save()
    water_desc16 = WaterNormDescription(description="Крупный рогатый скот, молодняк", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc16.save()
    water_desc17 = WaterNormDescription(description="Лошади", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc17.save()
    water_desc18 = WaterNormDescription(description="Свиньи", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc18.save()
    water_desc19 = WaterNormDescription(description="Овцы", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc19.save()
    water_desc20 = WaterNormDescription(description="Козы", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc20.save()
    water_desc21 = WaterNormDescription(description="Куры, индейки", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc21.save()
    water_desc22 = WaterNormDescription(description="Утки, гуси", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc22.save()
    water_desc23 = WaterNormDescription(description="Лошади, молодняк", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc23.save()
    water_desc24 = WaterNormDescription(description="Свиньи, молодняк", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
    water_desc24.save()
    
    # 4. Виды сельскохозяйственных животных
    water_desc25 = WaterNormDescription(description="Баня при наличии водопровода", direction_type=WaterNormDescription.DIRECTION_USING)
    water_desc25.save()
    water_desc26 = WaterNormDescription(description="Баня при водоснабжении из уличной колонки", direction_type=WaterNormDescription.DIRECTION_USING)
    water_desc26.save()
    water_desc27 = WaterNormDescription(description="Мойка мотоцикла", direction_type=WaterNormDescription.DIRECTION_USING)
    water_desc27.save()
    water_desc28 = WaterNormDescription(description="Мойка автомобиля при наличии водопровода", direction_type=WaterNormDescription.DIRECTION_USING)
    water_desc28.save()
    water_desc29 = WaterNormDescription(description="Мойка автомобиля при водоснабжении из уличной колонки", direction_type=WaterNormDescription.DIRECTION_USING)
    water_desc29.save()
    water_desc30 = WaterNormDescription(description="Полив земельного участка при наличии водопровода", direction_type=WaterNormDescription.DIRECTION_USING)
    water_desc30.save()
    water_desc31 = WaterNormDescription(description="Полив земельного участка при водоснабжении из уличной колонки", direction_type=WaterNormDescription.DIRECTION_USING)
    water_desc31.save()
    
    # Скор действия норматива по воде 
    WaterNormValidity.objects.all().delete()
    water_norm_val1 = WaterNormValidity(start='2013-12-01', end='2015-03-31')
    water_norm_val1.save()
    water_norm_val2 = WaterNormValidity(start='2015-04-01', end='2015-06-30')
    water_norm_val2.save()
    water_norm_val3 = WaterNormValidity(start='2015-07-01', end='2015-12-31')
    water_norm_val3.save()
    water_norm_val4 = WaterNormValidity(start='2016-01-01', end='2016-06-30')
    water_norm_val4.save()
    water_norm_val5 = WaterNormValidity(start='2016-07-01', end='2016-12-31')
    water_norm_val5.save()
    water_norm_val6 = WaterNormValidity(start='2017-01-01', end='2017-12-31')
    water_norm_val6.save()

    CommunalService.objects.all().delete()
    cold_water_service = CommunalService (name=CommunalService.COLD_WATER)
    cold_water_service.save()
    heating_service = CommunalService (name=CommunalService.HEATING)
    heating_service.save()
    
    cold_water_service = CommunalService.objects.get(name=CommunalService.COLD_WATER)
    # Норматив по ХОЛОДНОЙ воде (TODO: остальные заполнять по мере необходимости)
    # Степень благоустройства жилых помещений:
    # '2015-01-01' -> '2015-03-31'
    WaterNorm.objects.all().delete()
    water_norm1 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc1, validity=water_norm_val1, service=cold_water_service, value=5.193)
    water_norm1.save()
    water_norm2 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc2, validity=water_norm_val1, service=cold_water_service, value=6.470)
    water_norm2.save()
    water_norm3 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc3, validity=water_norm_val1, service=cold_water_service, value=5.145)
    water_norm3.save()
    water_norm4 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc4, validity=water_norm_val1, service=cold_water_service, value=6.470)
    water_norm4.save()
    water_norm5 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc5, validity=water_norm_val1, service=cold_water_service, value=4.619)
    water_norm5.save()
    water_norm6 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc6, validity=water_norm_val1, service=cold_water_service, value=6.470)
    water_norm6.save()
    water_norm7 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc7, validity=water_norm_val1, service=cold_water_service, value=4.183)
    water_norm7.save()
    water_norm8 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc8, validity=water_norm_val1, service=cold_water_service, value=6.470)
    water_norm8.save()
    water_norm9 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc9, validity=water_norm_val1, service=cold_water_service, value=3.529)
    water_norm9.save()
    water_norm10 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc10, validity=water_norm_val1, service=cold_water_service, value=5.167)
    water_norm10.save()
    water_norm11 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc11, validity=water_norm_val1, service=cold_water_service, value=4.255)
    water_norm11.save()
    water_norm12 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc12, validity=water_norm_val1, service=cold_water_service, value=1.055)
    water_norm12.save()
    water_norm13 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc13, validity=water_norm_val1, service=cold_water_service, value=2.879)
    water_norm13.save()
    # '2015-04-01'->'2015-06-30'
    water_norm14 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc1, validity=water_norm_val2, service=cold_water_service, value=5.712)
    water_norm14.save()
    water_norm15 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc2, validity=water_norm_val2, service=cold_water_service, value=7.117)
    water_norm15.save()
    water_norm16 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc3, validity=water_norm_val2, service=cold_water_service, value=5.660)
    water_norm16.save()
    water_norm17 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc4, validity=water_norm_val2, service=cold_water_service, value=7.117)
    water_norm17.save()
    water_norm18 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc5, validity=water_norm_val2, service=cold_water_service, value=5.081)
    water_norm18.save()
    water_norm19 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc6, validity=water_norm_val2, service=cold_water_service, value=7.117)
    water_norm19.save()
    water_norm20 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc7, validity=water_norm_val2, service=cold_water_service, value=4.601)
    water_norm20.save()
    water_norm21 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc8, validity=water_norm_val2, service=cold_water_service, value=7.117)
    water_norm21.save()
    water_norm22 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc9, validity=water_norm_val2, service=cold_water_service, value=3.882)
    water_norm22.save()
    water_norm23 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc10, validity=water_norm_val2, service=cold_water_service, value=5.684)
    water_norm23.save()
    water_norm24 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc11, validity=water_norm_val2, service=cold_water_service, value=4.681)
    water_norm24.save()
    water_norm25 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc12, validity=water_norm_val2, service=cold_water_service, value=1.161)
    water_norm25.save()
    water_norm26 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc13, validity=water_norm_val2, service=cold_water_service, value=3.167)
    water_norm26.save()
    # '2015-07-01'->'2015-12-31'
    water_norm27 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc1, validity=water_norm_val3, service=cold_water_service, value=6.232)
    water_norm27.save()
    water_norm28 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc2, validity=water_norm_val3, service=cold_water_service, value=7.764)
    water_norm28.save()
    water_norm29 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc3, validity=water_norm_val3, service=cold_water_service, value=6.174)
    water_norm29.save()
    water_norm30 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc4, validity=water_norm_val3, service=cold_water_service, value=7.764)
    water_norm30.save()
    water_norm31 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc5, validity=water_norm_val3, service=cold_water_service, value=5.543)
    water_norm31.save()
    water_norm32 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc6, validity=water_norm_val3, service=cold_water_service, value=7.764)
    water_norm32.save()
    water_norm33 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc7, validity=water_norm_val3, service=cold_water_service, value=5.020)
    water_norm33.save()
    water_norm34 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc8, validity=water_norm_val3, service=cold_water_service, value=7.764)
    water_norm34.save()
    water_norm35 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc9, validity=water_norm_val3, service=cold_water_service, value=4.235)
    water_norm35.save()
    water_norm36 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc10, validity=water_norm_val3, service=cold_water_service, value=6.200)
    water_norm36.save()
    water_norm37 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc11, validity=water_norm_val3, service=cold_water_service, value=5.106)
    water_norm37.save()
    water_norm38 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc12, validity=water_norm_val3, service=cold_water_service, value=1.266)
    water_norm38.save()
    water_norm39 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc13, validity=water_norm_val3, service=cold_water_service, value=3.455)
    water_norm39.save()
    
    #TODO: ОДН (общее имущество) заполнить по мере необходимости
    
    # Виды сельскохозяйственных животных
    # '2015-01-01' -> '2015-03-31'
    water_norm40 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc15, validity=water_norm_val1, service=cold_water_service, value=1.825)
    water_norm40.save()
    water_norm41 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc16, validity=water_norm_val1, service=cold_water_service, value=0.913)
    water_norm41.save()
    water_norm42 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc17, validity=water_norm_val1, service=cold_water_service, value=1.825)
    water_norm42.save()
    water_norm43 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc18, validity=water_norm_val1, service=cold_water_service, value=0.913)
    water_norm43.save()
    water_norm44 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc19, validity=water_norm_val1, service=cold_water_service, value=0.304)
    water_norm44.save()
    water_norm45 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc20, validity=water_norm_val1, service=cold_water_service, value=0.076)
    water_norm45.save()
    water_norm46 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc21, validity=water_norm_val1, service=cold_water_service, value=0.030)
    water_norm46.save()
    water_norm47 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc22, validity=water_norm_val1, service=cold_water_service, value=0.052)
    water_norm47.save()
    water_norm48 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc23, validity=water_norm_val1, service=cold_water_service, value=1.065)
    water_norm48.save()
    water_norm49 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc24, validity=water_norm_val1, service=cold_water_service, value=0.319)
    water_norm49.save()
    # '2015-04-01'->'2015-06-30'
    water_norm50 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc15, validity=water_norm_val2, service=cold_water_service, value=2.008)
    water_norm50.save()
    water_norm51 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc16, validity=water_norm_val2, service=cold_water_service, value=1.004)
    water_norm51.save()
    water_norm52 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc17, validity=water_norm_val2, service=cold_water_service, value=2.008)
    water_norm52.save()
    water_norm53 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc18, validity=water_norm_val2, service=cold_water_service, value=1.004)
    water_norm53.save()
    water_norm54 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc19, validity=water_norm_val2, service=cold_water_service, value=0.334)
    water_norm54.save()
    water_norm55 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc20, validity=water_norm_val2, service=cold_water_service, value=0.084)
    water_norm55.save()
    water_norm56 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc21, validity=water_norm_val2, service=cold_water_service, value=0.033)
    water_norm56.save()
    water_norm57 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc22, validity=water_norm_val2, service=cold_water_service, value=0.057)
    water_norm57.save()
    water_norm58 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc23, validity=water_norm_val2, service=cold_water_service, value=1.172)
    water_norm58.save()
    water_norm59 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc24, validity=water_norm_val2, service=cold_water_service, value=0.351)
    water_norm59.save()
    # '2015-07-01'->'2015-12-31'
    water_norm60 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc15, validity=water_norm_val3, service=cold_water_service, value=2.190)
    water_norm60.save()
    water_norm61 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc16, validity=water_norm_val3, service=cold_water_service, value=1.096)
    water_norm61.save()
    water_norm62 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc17, validity=water_norm_val3, service=cold_water_service, value=2.190)
    water_norm62.save()
    water_norm63 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc18, validity=water_norm_val3, service=cold_water_service, value=1.096)
    water_norm63.save()
    water_norm64 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc19, validity=water_norm_val3, service=cold_water_service, value=0.365)
    water_norm64.save()
    water_norm65 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc20, validity=water_norm_val3, service=cold_water_service, value=0.091)
    water_norm65.save()
    water_norm66 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc21, validity=water_norm_val3, service=cold_water_service, value=0.036)
    water_norm66.save()
    water_norm67 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc22, validity=water_norm_val3, service=cold_water_service, value=0.062)
    water_norm67.save()
    water_norm68 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc23, validity=water_norm_val3, service=cold_water_service, value=1.278)
    water_norm68.save()
    water_norm69 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc24, validity=water_norm_val3, service=cold_water_service, value=0.383)
    water_norm69.save()
    
    # Направления использования
    # '2015-01-01' -> '2015-03-31'
    water_norm70 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc25, validity=water_norm_val1, service=cold_water_service, value=0.217)
    water_norm70.save()
    water_norm71 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc26, validity=water_norm_val1, service=cold_water_service, value=0.130)
    water_norm71.save()
    water_norm72 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc27, validity=water_norm_val1, service=cold_water_service, value=3.800)
    water_norm72.save()
    water_norm73 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc28, validity=water_norm_val1, service=cold_water_service, value=65.200)
    water_norm73.save()
    water_norm74 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc29, validity=water_norm_val1, service=cold_water_service, value=9.900)
    water_norm74.save()
    water_norm75 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc30, validity=water_norm_val1, service=cold_water_service, value=0.185)
    water_norm75.save()
    water_norm76 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc31, validity=water_norm_val1, service=cold_water_service, value=0.061)
    water_norm76.save()
    # '2015-04-01'->'2015-06-30'
    water_norm77 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc25, validity=water_norm_val2, service=cold_water_service, value=0.239)
    water_norm77.save()
    water_norm78 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc26, validity=water_norm_val2, service=cold_water_service, value=0.143)
    water_norm78.save()
    water_norm79 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc27, validity=water_norm_val2, service=cold_water_service, value=4.180)
    water_norm79.save()
    water_norm80 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc28, validity=water_norm_val2, service=cold_water_service, value=71.720)
    water_norm80.save()
    water_norm81 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc29, validity=water_norm_val2, service=cold_water_service, value=10.890)
    water_norm81.save()
    water_norm82 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc30, validity=water_norm_val2, service=cold_water_service, value=0.204)
    water_norm82.save()
    water_norm83 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc31, validity=water_norm_val2, service=cold_water_service, value=0.067)
    water_norm83.save()
    # '2015-07-01'->'2015-12-31'
    water_norm84 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc25, validity=water_norm_val3, service=cold_water_service, value=0.260)
    water_norm84.save()
    water_norm85 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc26, validity=water_norm_val3, service=cold_water_service, value=0.156)
    water_norm85.save()
    water_norm86 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc27, validity=water_norm_val3, service=cold_water_service, value=4.560)
    water_norm86.save()
    water_norm87 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc28, validity=water_norm_val3, service=cold_water_service, value=78.240)
    water_norm87.save()
    water_norm88 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc29, validity=water_norm_val3, service=cold_water_service, value=11.880)
    water_norm88.save()
    water_norm89 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc30, validity=water_norm_val3, service=cold_water_service, value=0.222)
    water_norm89.save()
    water_norm90 = WaterNorm(subject_rf=subjectRF, norm_description=water_desc31, validity=water_norm_val3, service=cold_water_service, value=0.073)
    water_norm90.save()
    
    # Скор действия норматива по отоплению
    HeatingNormValidity.objects.all().delete()
    heating_norm_validity = HeatingNormValidity(start='2015-01-01', end='2015-12-31')
    heating_norm_validity.save()
    # Нормативы по отоплению для Тогучинского района
    HeatingNorm.objects.all().delete()
    heating_norm1 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_TO_1999, floor_amount=1, value=0.0474)
    heating_norm1.save()
    heating_norm2 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_TO_1999, floor_amount=2, value=0.0459)
    heating_norm2.save()
    heating_norm3 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_TO_1999, floor_amount=3, value=0.0302)
    heating_norm3.save()
    heating_norm4 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_TO_1999, floor_amount=4, value=0.0302)
    heating_norm4.save()
    heating_norm5 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_TO_1999, floor_amount=5, value=0.0260)
    heating_norm5.save()
    heating_norm6 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_FROM_2000, floor_amount=1, value=0.0204)
    heating_norm6.save()
    heating_norm7 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_FROM_2000, floor_amount=2, value=0.0205)
    heating_norm7.save()
    heating_norm8 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_FROM_2000, floor_amount=3, value=0.0199)
    heating_norm8.save()
    heating_norm9 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_FROM_2000, floor_amount=4, value=0.0156)
    heating_norm9.save()
    heating_norm10 = HeatingNorm(municipal_area=municipal_area, validity=heating_norm_validity, commissioning_type=HeatingNorm.COMMISIONING_FROM_2000, floor_amount=5, value=0.0156)
    heating_norm10.save()

    fill_total_info()
        
    fill_period()
    
    CalculationService.objects.all().delete()
    
    preapare_water_counter()

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'
    def handle(self, *args, **options):
        prepare_db_base()
        self.stdout.write('DB has just prepared successfully.')

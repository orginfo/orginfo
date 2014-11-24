from django.core.management.base import BaseCommand
from accounting.models import Period, Region, RealEstate, ServiceClient, ColdWaterNorm, DegreeOfImprovementsDwelling, ColdWaterReading, AnimalType, Animals, ColdWaterVolume, ColdWaterVolumeODN, Organization, ColdWaterNormODN, NormValidity, UserOrganization, Account, Payment
from django.contrib.auth.models import User
from django.db.models import Q
import datetime

#MYABE: перенести в отдельный модуль функцию заколнения
#базы данных.
def prepare_db_base():
    User.objects.filter(~Q(username="admin")).delete()
    User.objects.create_user(username="aa", password="aa")

    Period.objects.all().delete()
    period1 = Period(serial_number=1, start=datetime.date(2000, 12, 26), end=datetime.date(2001, 1, 25))
    period1.save()
    period2 = Period(serial_number=2, start=datetime.date(2001, 1, 26), end=datetime.date(2001, 2, 25))
    period2.save()
    period3 = Period(serial_number=3, start=datetime.date(2001, 2, 26), end=datetime.date(2001, 3, 25))
    period3.save()
    period4 = Period(serial_number=4, start=datetime.date(2001, 3, 26), end=datetime.date(2001, 4, 25))
    period4.save()
    period5 = Period(serial_number=5, start=datetime.date(2001, 4, 26), end=datetime.date(2001, 5, 25))
    period5.save()
    period6 = Period(serial_number=6, start=datetime.date(2001, 5, 26), end=datetime.date(2001, 6, 25))
    period6.save()
    period7 = Period(serial_number=7, start=datetime.date(2001, 6, 26), end=datetime.date(2001, 7, 25))
    period7.save()

    Region.objects.all().delete()
    region = Region(name="Новосибирская область, Тогучинский район")
    region.save()

    Organization.objects.all().delete()
    organization = Organization(name="ООО Всем МУП-ам МУП")
    organization.save()

    UserOrganization.objects.all().delete()
    user_organization = UserOrganization(user=User.objects.filter(username="aa").get(), organization=organization)
    user_organization.save()

    DegreeOfImprovementsDwelling.objects.all().delete()
    degree_of_improvements = DegreeOfImprovementsDwelling(name="Максимальная комплектация")
    degree_of_improvements.save()

    RealEstate.objects.all().delete()
    lenina_d1 = RealEstate(address="ул. Ленина, д. 1", region=region, parent=None, cold_water_counter_setup_date=datetime.date(2001, 1, 1), type=RealEstate.BUILDING_TYPE, space=100, space_of_joint_estate=10, residential=True, residents=-1, organization=organization, degree_of_improvements=degree_of_improvements) #residential=None?
    lenina_d1.save()
    lenina_d1_kv1 = RealEstate(address="ул. Ленина, д. 1, кв. 1", region=region, parent=lenina_d1, cold_water_counter_setup_date=datetime.date(2001, 1, 13), type=RealEstate.FLAT_TYPE, space=30, space_of_joint_estate=-1, residential=True, residents=2, organization=organization, degree_of_improvements=degree_of_improvements)
    lenina_d1_kv1.save()
    lenina_d1_kv2 = RealEstate(address="ул. Ленина, д. 1, кв. 2", region=region, parent=lenina_d1, cold_water_counter_setup_date=datetime.date(2001, 1, 13), type=RealEstate.FLAT_TYPE, space=50, space_of_joint_estate=-1, residential=True, residents=3, organization=organization, degree_of_improvements=degree_of_improvements)
    lenina_d1_kv2.save()
    lenina_d2 = RealEstate(address="ул. Ленина, д. 2", region=region, parent=None, cold_water_counter_setup_date=datetime.date(2001, 1, 2), type=RealEstate.HOUSE_TYPE, space=110, space_of_joint_estate=-1, residential=True, residents=3, organization=organization, degree_of_improvements=degree_of_improvements)
    lenina_d2.save()

    Account.objects.all().delete()
    Account(real_estate=lenina_d1_kv1, balance=0, owners="Андреев А.А.").save()
    lenina_d1_kv2_account = Account(real_estate=lenina_d1_kv2, balance=1000.01, owners="Баранов Б.Б. Баранова Б.Б.")
    lenina_d1_kv2_account.save()
    Account(real_estate=lenina_d2, balance=0, owners="Воробьев В.В.").save()

    Payment.objects.all().delete()
    Payment(amount=100, balance_before_payment=1000.01, account=lenina_d1_kv2_account, date=datetime.date(2014, 12, 31), comment=None).save()

    ServiceClient.objects.all().delete()
    ServiceClient(real_estate=lenina_d1, service_name=ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 1, 1), end=None).save()
    ServiceClient(real_estate=lenina_d1_kv1, service_name=ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 1, 1), end=None).save()
    ServiceClient(real_estate=lenina_d1_kv2, service_name=ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 1, 1), end=None).save()
    ServiceClient(real_estate=lenina_d2, service_name=ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 1, 1), end=None).save()

    NormValidity.objects.all().delete()
    norm_validity = NormValidity(start=datetime.date(2013, 1, 1), end=datetime.date(2014, 12, 31))
    norm_validity.save()

    ColdWaterNorm.objects.all().delete()
    ColdWaterNorm(region=region, degree_of_improvements=degree_of_improvements, validity=norm_validity, norm=10.2).save()

    ColdWaterReading.objects.all().delete()
    ColdWaterReading(period=period7, value=10210, real_estate=lenina_d1, date=datetime.date(2001, 7, 22)).save()

    ColdWaterNormODN.objects.all().delete()
    ColdWaterNormODN(region=region, validity=norm_validity, norm=1.2)

    #Эти таблицы заполняются роботом:
    ColdWaterVolume.objects.all().delete()
    ColdWaterVolumeODN.objects.all().delete()

    AnimalType.objects.all().delete()
    goose = AnimalType(name="Гусь", norm=0.5)
    goose.save()
    boar = AnimalType(name="Кабан", norm=12.2)
    boar.save()

    Animals.objects.all().delete()
    Animals(count=12, real_estate=lenina_d2, type=goose)
    Animals(count=2, real_estate=lenina_d2, type=boar)

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'
    def handle(self, *args, **options):
        prepare_db_base()
        self.stdout.write('DB has just prepared successfully.')

from django.core.management.base import BaseCommand
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality, Street

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
    loc1 = Locality(name="Боровлянка", type=Locality.VILLAGE, municipal_area=municipal_area, municipal_union=union1)
    loc1.save()
    loc2 = Locality(name="Зверобойка", type=Locality.SETTLEMENT, municipal_area=municipal_area, municipal_union=union1)
    loc2.save()
    loc3 = Locality(name="Кудельный Ключ", type=Locality.HAMLET, municipal_area=municipal_area, municipal_union=union1)
    loc3.save()
    loc4 = Locality(name="Прямушка", type=Locality.SETTLEMENT, municipal_area=municipal_area, municipal_union=union1)
    loc4.save()
    loc5 = Locality(name="Шубкино", type=Locality.HAMLET, municipal_area=municipal_area, municipal_union=union1)
    loc5.save()
    loc6 = Locality(name="Нечаевский", type=Locality.SETTLEMENT, municipal_area=municipal_area, municipal_union=union2)
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
    street7 = Street(name="Молодёжная", locality=loc3)
    street7.save()
    street8 = Street(name="Береговая", locality=loc3)
    street8.save()
    street9 = Street(name="Весенняя", locality=loc3)
    street9.save()
    street10 = Street(name="Новая", locality=loc3)
    street10.save()
    street11 = Street(name="Зелёная", locality=loc3)
    street11.save()
    street12 = Street(name="Заречная", locality=loc3)
    street12.save()
    street13 = Street(name="Центральная", locality=loc4)
    street13.save()
    street14 = Street(name="Центральная", locality=loc5)
    street14.save()
    street15 = Street(name="Школьная", locality=loc5)
    street15.save()
    street16 = Street(name="Зелёная", locality=loc5)
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

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'
    def handle(self, *args, **options):
        prepare_db_base()
        self.stdout.write('DB has just prepared successfully.')

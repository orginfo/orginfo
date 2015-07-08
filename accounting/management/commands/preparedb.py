from django.core.management.base import BaseCommand
from accounting.models import SubjectRF, MunicipalArea, MunicipalUnion, Locality

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

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'
    def handle(self, *args, **options):
        prepare_db_base()
        self.stdout.write('DB has just prepared successfully.')

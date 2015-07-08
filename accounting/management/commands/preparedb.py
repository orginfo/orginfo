from django.core.management.base import BaseCommand
from accounting.models import SubjectRF, MunicipalArea

def prepare_db_base():
    # Субъект РФ
    SubjectRF.objects.all().delete()
    subjectRF = SubjectRF(name="Новосибирская область")
    subjectRF.save()

    # Муниципальный район
    MunicipalArea.objects.all().delete()
    municipal_area = MunicipalArea(name="Тогучинский район", subject_rf=subjectRF)
    municipal_area.save()

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'
    def handle(self, *args, **options):
        prepare_db_base()
        self.stdout.write('DB has just prepared successfully.')

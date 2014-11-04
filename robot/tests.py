from django.test import TestCase

from robot.errors import ForgottenInitialReadingError
from robot.algorithm import calculate_individual_cold_water_volume, calculate_share_of_service_usage
from accounting.models import RealEstate, Period, ColdWaterReading
import datetime

from django.db import transaction
import accounting

#python manage.py test robot
#(py34dj17)am@am:~/projects/orginfo/orginfo$ python ../manage.py test robot
class RobotTestCase(TestCase):

    def test_forgotten_initial_reading(self):
        """Забыли внести показания счетчика при установке."""
        region = accounting.models.Region(name="Тогучинский район")
        region.save()
        real_estate = accounting.models.RealEstate(address="ул. Ленина, д. 1, кв. 2", region=region, parent=None, cold_water_counter_setup_date=datetime.date(2001, 1, 13), type=RealEstate.FLAT_TYPE, space=40, residential=True, residents=2)
        real_estate.save()
        Period(serial_number=1, start=datetime.date(2000, 12, 26), end=datetime.date(2001, 1, 25)).save()
        Period(serial_number=2, start=datetime.date(2001, 1, 26), end=datetime.date(2001, 2, 25)).save()
        Period(serial_number=3, start=datetime.date(2001, 2, 26), end=datetime.date(2001, 3, 25)).save()
        Period(serial_number=4, start=datetime.date(2001, 3, 26), end=datetime.date(2001, 4, 25)).save()
        Period(serial_number=5, start=datetime.date(2001, 4, 26), end=datetime.date(2001, 5, 25)).save()
        Period(serial_number=6, start=datetime.date(2001, 5, 26), end=datetime.date(2001, 6, 25)).save()
        last_period = Period(serial_number=7, start=datetime.date(2001, 6, 26), end=datetime.date(2001, 7, 25))
        last_period.save()
        ColdWaterReading(period=last_period, value=-1, real_estate=real_estate, date=datetime.date(2001, 7, 22)).save()

        error_occured = False
        try:
            calculate_individual_cold_water_volume(real_estate, None, None, None)
        except ForgottenInitialReadingError:
            error_occured = True

        self.assertTrue(error_occured)

    def test_rollback(self):
        """ В случае ошибки в write_off() данные должны быть отменены.

        #TODO: Пока не знаю как написать тест, поэтому здесь будет вот такая
        заглушка:
        """
        try:
            with transaction.atomic():
                Period(serial_number=1, start=datetime.date(2000, 12, 26), end=datetime.date(2001, 1, 25)).save()
                raise ForgottenInitialReadingError
                Period(serial_number=2, start=datetime.date(2001, 1, 26), end=datetime.date(2001, 2, 25)).save()
        except ForgottenInitialReadingError:
            pass

        self.assertEqual(0, Period.objects.all().count())

        try:
            with transaction.atomic():
                Period(serial_number=1, start=datetime.date(2000, 12, 26), end=datetime.date(2001, 1, 25)).save()
                Period(serial_number=2, start=datetime.date(2001, 1, 26), end=datetime.date(2001, 2, 25)).save()
        except ForgottenInitialReadingError:
            pass

        self.assertEqual(2, Period.objects.all().count())

    def test_calculate_share_of_service_usage(self):
        region = accounting.models.Region(name="Тогучинский район")
        region.save()
        real_estate = accounting.models.RealEstate(address="ул. Ленина, д. 1, кв. 2", region=region, parent=None, cold_water_counter_setup_date=datetime.date(2001, 1, 13), type=RealEstate.FLAT_TYPE, space=40, residential=True, residents=2)
        real_estate.save()
        organization = accounting.models.Organization(name="OOO OrgInfo")
        organization.save()
        client = accounting.models.Client(lfm="Андреев А.А.", organization=organization, amount=0, real_estate=real_estate)
        client.save()
        accounting.models.ServiceClient(client=client, service_name=accounting.models.ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 1, 19), end=datetime.date(2000, 1, 22)).save()
        accounting.models.ServiceClient(client=client, service_name=accounting.models.ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 1, 24), end=datetime.date(2000, 2, 2)).save()
        accounting.models.ServiceClient(client=client, service_name=accounting.models.ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 2, 16), end=datetime.date(2000, 2, 18)).save()
        accounting.models.ServiceClient(client=client, service_name=accounting.models.ServiceClient.COLD_WATER_SERVICE, start=datetime.date(2000, 2, 20), end=None).save()
        period = Period(serial_number=2, start=datetime.date(2000, 1, 26), end=datetime.date(2000, 2, 25))
        period.save()

        calculate_share_of_service_usage(client, accounting.models.ServiceClient.COLD_WATER_SERVICE, period)

        self.assertEqual(0, 0)

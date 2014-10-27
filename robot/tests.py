from django.test import TestCase

from robot.errors import ForgottenInitialReadingError
from robot.algorithm import calculate_individual_cold_water_volume
from accounting.models import RealEstate, Period, ColdWaterReading
import datetime

#python manage.py test robot
#(py34dj17)am@am:~/projects/orginfo/orginfo$ python ../manage.py test robot
class RobotTestCase(TestCase):

    def test_synthetic(self):
        """Синтетический тест.

        Синтетический тест служит кирпичеком в архитектуре программы, после ее
        становления будет заменен функциональными тестами.
        http://djbook.ru/rel1.6/intro/tutorial05.html#create-a-test-to-expose-the-bug
        """
        self.assertEqual(True, False)

    def test_forgotten_initial_reading(self):
        """Забыли внести показания счетчика при установке."""
        real_estate = RealEstate(address="ул. Ленина, д. 1, кв. 2", parent=None, cold_water_counter_setup_date=datetime.date(2001, 1, 13), type=RealEstate.FLAT_TYPE)
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

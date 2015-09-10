from django.test import TestCase
from accounting.models import WaterNormDescription, MunicipalUnion, SubjectRF, MunicipalArea, Locality, Street, HouseAddress, RealEstate, HomeownershipHistory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import json
from datetime import date
import mock

#./manage.py test accounting
class FakeDate(date):
    "A manipulable date replacement"
    def __new__(cls, *args, **kwargs):
        return date.__new__(date, *args, **kwargs)

class HomeownershipHistoryTests(TestCase):
    def setUp(self):
        User.objects.create_user('nn', 'lennon@thebeatles.com', 'nn')
        self.maxDiff = None

    def test_empty_periods(self):
        self.assertEqual(False, True)

    @mock.patch('datetime.date', FakeDate)
    def test_one_change_two_periods(self):
        """
        +--------------------------------------------------+
        | Расчётный период | Август 2015   | Сентябрь 2015 |
        +--------------------------------------------------+
        | Изм-но с         |       |←22.08 |←26.08         |
        +--------------------------------------------------+
        | Лошади           |       |          4            |
        +--------------------------------------------------+
        """
        water_desc17 = WaterNormDescription(description="Лошади", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
        water_desc17.save()
        subjectRF = SubjectRF(name="Новосибирская область")
        subjectRF.save()
        municipal_area = MunicipalArea(name="Тогучинский район", subject_rf=subjectRF)
        municipal_area.save()
        union1 = MunicipalUnion(name="Кудельно-Ключевской сельсовет", municipal_area=municipal_area)
        union1.save()
        loc3 = Locality(name="Кудельный Ключ", type=Locality.HAMLET, subject_rf=subjectRF, municipal_area=municipal_area, municipal_union=union1)
        loc3.save()
        street4 = Street(name="Лесная", locality=loc3)
        street4.save()
        address = HouseAddress(index="633447", street=street4, house_number=20)
        address.save()
        real_estate = RealEstate(address=address, number="")
        real_estate.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22')
        homeownership_history.save()

        #print(HomeownershipHistory.objects.all()[0].start)
        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": "Август 2015",
                "length": 2
            }, {
                "name": "Сентябрь 2015"
            }],
            [{
                "name": "Изм-но с"
            }, {
                "name": ""
            }, {
                "name": "←22.08"
            }, {
                "name": "←26.08"
            }],
            [{
                "name": "Лошади"
            }, {
                "name": ""
            }, {
                "name": 4.0,
                "length": 2
            }]
        ]
        FakeDate.today = classmethod(lambda cls: date(2015, 9, 3))
        self.client.login(username='nn', password='nn')
        response = self.client.get(reverse('accounting:homeownership_history'))
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

    def test_one_change_three_periods(self):
        """
        +----------------------------------------------------+--------------+
        | Расчётный период | Август 2015    | Сентябрь 2015 | Октябрь 2015 |
        +---------------------------------------------------+--------------+
        | Изм-но с         |        |←22.08 |←26.08         | ←26.09       |
        +---------------------------------------------------+--------------+
        | Лошади           |        |                   4                  |
        +------------------------------------------------------------------+
        """
        self.assertEqual(False, True)

    def test_two_changes_three_periods(self):
        """
        +----------------------------------------------------+--------------+
        | Расчётный период | Август 2015     | Сентябрь 2015 | Октябрь 2015 |
        +----------------------------------------------------+--------------+
        | Изм-но с         |        |←22.08  |←26.08         | ←26.09       |
        +----------------------------------------------------+--------------+
        | Лошади           |        |           4            |      8       |
        +----------------------------------------------------+--------------+
        """
        self.assertEqual(False, True)

    def test_many_changes_three_periods_and_before(self):
        """
        +------------------+-----------------------+-----------------------------------------------+-----------------------+
        | Расчётный период |   раньше Июнь 2015    |                    Июль 2015                  |      Август 2015      |
        +------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
        | Изм-но с         |       |←22.06 |←24.06 |←26.06 |←28.06 |←14.07 |←15.07 |←16.07 |←20.07 |←29.07 |←01.08 |←03.08 |
        +------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
        | Лошади           |           4           |                               |            2          |       4       |
        +------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
        | Коровы           |       |           2           |           4           |       5       |       4       |   5   |
        +------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
        | Куры             |       15      |   8   |       30      |   19  |   30  |   4   |          18           |   30  |
        +------------------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
        """
        self.assertEqual(False, True)

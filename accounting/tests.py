from django.test import TestCase
from accounting.models import WaterNormDescription, MunicipalUnion, SubjectRF, MunicipalArea, Locality, Street, HouseAddress, RealEstate, HomeownershipHistory
from accounting.views import get_period, get_period_name
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import json
from datetime import date, datetime
import pytz
import mock

#./manage.py test accounting
class FakeDate(date):
    "A manipulable date replacement"
    def __new__(cls, *args, **kwargs):
        return date.__new__(date, *args, **kwargs)

class HomeownershipHistoryTests(TestCase):
    def setUp(self):
        User.objects.create_user('nn', 'lennon@thebeatles.com', 'nn')
        self.period_names = {
            "july2015": get_period_name(get_period(date(2015, 7, 1))),
            "august2015": get_period_name(get_period(date(2015, 8, 1))),
            "september2015": get_period_name(get_period(date(2015, 9, 1))),
            "october2015": get_period_name(get_period(date(2015, 10, 1)))
        }
        self.novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")

    @mock.patch('datetime.date', FakeDate)
    def test_empty_periods(self):
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

        FakeDate.today = classmethod(lambda cls: date(2015, 9, 3))
        self.client.login(username='nn', password='nn')
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertEqual("table" in response.context, False)

    @mock.patch('datetime.date', FakeDate)
    def test_first_date_as_start_period(self):
        """
        +------------------+-----------+-------------+---------------+
        | Расчётный период | Июль 2015 | Август 2015 | Сентябрь 2015 |
        +------------------+-----------+-------------+---------------+
        | Изм-но с         |←26.06     |←26.07       |←26.08         |
        +------------------+-----------+-------------+---------------+
        | Лошади           |           |        4                    |
        +------------------+-----------+-----------------------------+
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
        t20150701_2300 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-07-26', updated=t20150701_2300)
        homeownership_history.save()

        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["july2015"],
            }, {
                "name": self.period_names["august2015"],
            }, {
                "name": self.period_names["september2015"]
            }],
            [{
                "name": "Изм-но с"
            }, {
                "name": ""
            }, {
                "name": "←26.07"
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
        FakeDate.today = classmethod(lambda cls: date(2015, 9, 18))
        self.client.login(username='nn', password='nn')
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)


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
        t20150701_2300 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22', updated=t20150701_2300)
        homeownership_history.save()

        #print(HomeownershipHistory.objects.all()[0].start)
        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["august2015"],
                "length": 2
            }, {
                "name": self.period_names["september2015"]
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
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

    @mock.patch('datetime.date', FakeDate)
    def test_exclude_start_in_second_period(self):
        """
        +------------------+---------------+---------------+
        | Расчётный период | Август 2015   | Сентябрь 2015 |
        +------------------+-------+-------+---------------+
        | Изм-но с         |       |←22.08 |←28.08         |
        +------------------+-------+-------+---------------+
        | Лошади           |       |   4   |       5       |
        +------------------+-------+-------+---------------+
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
        t20150701_2300 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22', updated=t20150701_2300)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=5, start='2015-08-28', updated=t20150701_2300)
        homeownership_history.save()

        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["august2015"],
                "length": 2
            }, {
                "name": self.period_names["september2015"]
            }],
            [{
                "name": "Изм-но с"
            }, {
                "name": ""
            }, {
                "name": "←22.08"
            }, {
                "name": "←28.08"
            }],
            [{
                "name": "Лошади"
            }, {
                "name": ""
            }, {
                "name": 4.0
            }, {
                "name": 5.0
            }]
        ]
        FakeDate.today = classmethod(lambda cls: date(2015, 9, 3))
        self.client.login(username='nn', password='nn')
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

    @mock.patch('datetime.date', FakeDate)
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
        t20150701_2300 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22', updated=t20150701_2300)
        homeownership_history.save()

        #print(HomeownershipHistory.objects.all()[0].start)
        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["august2015"],
                "length": 2
            }, {
                "name": self.period_names["september2015"]
            }, {
                "name": self.period_names["october2015"]
            }],
            [{
                "name": "Изм-но с"
            }, {
                "name": ""
            }, {
                "name": "←22.08"
            }, {
                "name": "←26.08"
            }, {
                "name": "←26.09"
            }],
            [{
                "name": "Лошади"
            }, {
                "name": ""
            }, {
                "name": 4.0,
                "length": 3
            }]
        ]
        FakeDate.today = classmethod(lambda cls: date(2015, 10, 3))
        self.client.login(username='nn', password='nn')
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

    @mock.patch('datetime.date', FakeDate)
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
        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["august2015"],
                "length": 2
            }, {
                "name": self.period_names["september2015"]
            }, {
                "name": self.period_names["october2015"]
            }],
            [{
                "name": "Изм-но с"
            }, {
                "name": ""
            }, {
                "name": "←22.08"
            }, {
                "name": "←26.08"
            }, {
                "name": "←26.09"
            }],
            [{
                "name": "Лошади"
            }, {
                "name": ""
            }, {
                "name": 4.0,
                "length": 2
            }, {
                "name": 8.0
            }]
        ]

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
        t20150701_2300 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history1 = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22', updated=t20150701_2300)
        homeownership_history1.save()
        homeownership_history2 = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=8, start='2015-09-26', updated=t20150701_2300)
        homeownership_history2.save()

        FakeDate.today = classmethod(lambda cls: date(2015, 10, 3))
        self.client.login(username='nn', password='nn')
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

    @mock.patch('datetime.date', FakeDate)
    def test_two_kind_of_animals(self):
        """
        +----------------------+-----------------------+---------------+
        | Расчётный период     |      Август 2015      | Сентябрь 2015 |
        +----------------------+-------+---------------+---------------+
        | Изм-но с             |       |←22.08 |←23.08 |←28.08         |
        +----------------------+-------+-------+-------+---------------+
        | Лошади               |       |      4        |       5       |
        +----------------------+-------+-------+-------+---------------+
        | Крупный рогатый скот |               |           3           |
        +----------------------+---------------+-----------------------+
        """
        water_desc15 = WaterNormDescription(description="Крупный рогатый скот", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
        water_desc15.save()
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
        t20150701_2300 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22', updated=t20150701_2300)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=5, start='2015-08-28', updated=t20150701_2300)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc15, count=3, start='2015-08-23', updated=t20150701_2300)
        homeownership_history.save()

        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["august2015"],
                "length": 3
            }, {
                "name": self.period_names["september2015"]
            }],
            [{
                "name": "Изм-но с"
            }, {
                "name": ""
            }, {
                "name": "←22.08"
            }, {
                "name": "←23.08"
            }, {
                "name": "←28.08"
            }],
            [{
                "name": "Крупный рогатый скот"
            }, {
                "name": "",
                "length": 2
            }, {
                "name": 3.0,
                "length": 2
            }],
            [{
                "name": "Лошади"
            }, {
                "name": ""
            }, {
                "name": 4.0,
                "length": 2
            }, {
                "name": 5.0
            }]
        ]
        FakeDate.today = classmethod(lambda cls: date(2015, 9, 3))
        self.client.login(username='nn', password='nn')
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

    @mock.patch('datetime.date', FakeDate)
    def test_one_change_date_two_periods_for_all_kind_of_animals(self):
        """
        +----------------------+---------------+---------------+
        | Расчётный период     | Август 2015   | Сентябрь 2015 |
        +----------------------+-------+-------+---------------+
        | Изм-но с             |       |←22.08 |←26.08         |
        +----------------------+-------+-----------------------+
        | Лошади               |       |          4            |
        +----------------------+-------+-----------------------+
        | Крупный рогатый скот |       |          3            |
        +----------------------+-------+-----------------------+
        """
        water_desc15 = WaterNormDescription(description="Крупный рогатый скот", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
        water_desc15.save()
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
        t20150701_2300 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22', updated=t20150701_2300)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc15, count=3, start='2015-08-22', updated=t20150701_2300)
        homeownership_history.save()

        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["august2015"],
                "length": 2
            }, {
                "name": self.period_names["september2015"]
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
                "name": "Крупный рогатый скот"
            }, {
                "name": ""
            }, {
                "name": 3.0,
                "length": 2
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
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

    @mock.patch('datetime.date', FakeDate)
    def test_two_kind_of_animals_updated(self):
        """
        До:
        +----------------------+-----------------------+---------------+--------------+
        | Расчётный период     |      Август 2015      | Сентябрь 2015 | Октябрь 2015 |
        +----------------------+-------+---------------+---------------+--------------+
        | Изм-но с             |       |←22.08 |←23.08 |←28.08         |←29.09        |
        +----------------------+-------+-------+-------+---------------+--------------+
        | Лошади               |       |      4        |       5       |      8       |
        +----------------------+-------+-------+-------+---------------+--------------+
        | Крупный рогатый скот |               |           3                          |
        +----------------------+---------------+-----------------------+--------------+
        После:
        +----------------------+-----------------------+---------------+--------------+
        | Расчётный период     |      Август 2015      | Сентябрь 2015 | Октябрь 2015 |
        +----------------------+-------+---------------+---------------+--------------+
        | Изм-но с             |       |←22.08 |←23.08 |←28.08         |←26.09        |
        +----------------------+-------+-------+-------+---------------+--------------+
        | Лошади               |       |      4        |                6             |
        +----------------------+-------+-------+-------+---------------+--------------+
        | Крупный рогатый скот |               |   3   |               4              |
        +----------------------+---------------+-------+---------------+--------------+
        """
        water_desc15 = WaterNormDescription(description="Крупный рогатый скот", direction_type=WaterNormDescription.AGRICULTURAL_ANIMALS)
        water_desc15.save()
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
        t2015_07_01 = self.novosibirsk_tz.localize(datetime(2015, 7, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=4, start='2015-08-22', updated=t2015_07_01)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=5, start='2015-08-28', updated=t2015_07_01)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=8, start='2015-09-29', updated=t2015_07_01)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc15, count=3, start='2015-08-23', updated=t2015_07_01)
        homeownership_history.save()
        t2015_08_01 = self.novosibirsk_tz.localize(datetime(2015, 8, 1, 23, 0, 0))
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc17, count=6, start='2015-08-28', updated=t2015_08_01)
        homeownership_history.save()
        homeownership_history = HomeownershipHistory(real_estate=real_estate, water_description=water_desc15, count=4, start='2015-08-28', updated=t2015_08_01)
        homeownership_history.save()

        expected_data = [
            [{
                "name": "Расчётный период"
            }, {
                "name": self.period_names["august2015"],
                "length": 3
            }, {
                "name": self.period_names["september2015"]
            }, {
                "name": self.period_names["october2015"]
            }],
            [{
                "name": "Изм-но с"
            }, {
                "name": ""
            }, {
                "name": "←22.08"
            }, {
                "name": "←23.08"
            }, {
                "name": "←28.08"
            }, {
                "name": "←26.09"
            }],
            [{
                "name": "Крупный рогатый скот"
            }, {
                "name": "",
                "length": 2
            }, {
                "name": 3.0
            }, {
                "name": 4.0,
                "length": 2
            }],
            [{
                "name": "Лошади"
            }, {
                "name": ""
            }, {
                "name": 4.0,
                "length": 2
            }, {
                "name": 6.0,
                "length": 2
            }]
        ]
        FakeDate.today = classmethod(lambda cls: date(2015, 10, 3))
        self.client.login(username='nn', password='nn')
        url = "%s?real_estate=%d" % (reverse('accounting:homeownership_history'), 1)
        response = self.client.get(url)
        self.assertJSONEqual(json.dumps(response.context['table']), json.dumps(expected_data), msg=None)

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

from django.test import TestCase

#python manage.py test robot
class RobotTestCase(TestCase):

    def test_synthetic(self):
        """Синтетический тест.

        Синтетический тест служит кирпичеком в архитектуре программы, после ее
        становления будет заменен функциональными тестами.
        http://djbook.ru/rel1.6/intro/tutorial05.html#create-a-test-to-expose-the-bug
        """
        self.assertEqual(True, False)

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from loan.api.serializers import LoanSerializer


class LoanSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('aunicorndev','aunicorndeveloper@gmail.com', 'errornotfound')
        self.valid_serializer_data = {
            "notional": 3500,
            "term": "Weekly",
            "frequency": 17,
            "start_date": "19-03-2024"
        }
        self.invalid_serializer_data = {
            "notional": -3500,
            "term": "Mont",
            "frequency": 0,
            "start_date": "2024-11-12"
        }
    def test_model_creation_valid_serializer_data(self):
        serializer = LoanSerializer(data=self.valid_serializer_data)
        self.assertTrue(serializer.is_valid())


    def test_model_creation_invalid_serializer_data(self):
        serializer = LoanSerializer(data=self.invalid_serializer_data)
        self.assertFalse(serializer.is_valid())
        self.assertEquals(serializer.errors['notional'][0], "Notional cannot be negative or 0.")
        self.assertEquals(serializer.errors['frequency'][0], "Frequency cannot be negative or 0.")
        self.assertEquals(serializer.errors['term'][0], "\"Mont\" is not a valid choice.")
        self.assertEquals(serializer.errors['start_date'][0],
                          "Date has wrong format. Use one of these formats instead: DD-MM-YYYY.")





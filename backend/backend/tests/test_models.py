import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from loan.models import Loan, Payment,Repayment



class LoanTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('aunicorndev','aunicorndeveloper@gmail.com', 'errornotfound')
    def test_model_creation(self):
        obj = Loan.objects.create(frequency = 3, start_date = datetime.date(2024,12,6), term= 'Weekly',
                                  notional = 1200,created_by=self.user)
        self.assertEqual(obj.frequency, 3)
        self.assertEqual(obj.start_date, datetime.date(2024,12,6))
        self.assertEqual(obj.term,'Weekly' )
        self.assertEqual(obj.notional, 1200.00)
        self.assertEqual(obj.created_by_id, 1)

    def test_model_validation_startdate_not_present(self):
        with self.assertRaises(IntegrityError):
            Loan.objects.create(frequency=3, term='Weekly',
                                      notional=1200, created_by=self.user)

    def test_model_validation_frequency_not_present(self):
        with self.assertRaises(IntegrityError):
            Loan.objects.create(start_date=datetime.date(2024, 12, 6), term='Weekly',
                                notional=1200, created_by=self.user)

    def test_model_validation_notional_not_present(self):
        with self.assertRaises(IntegrityError):
            Loan.objects.create(frequency=3, start_date=datetime.date(2024, 12, 6), term='Weekly',
                                created_by=self.user)

    def test_model_validation_created_by_not_present(self):
        with self.assertRaises(IntegrityError):
            Loan.objects.create(frequency=3, start_date=datetime.date(2024, 12, 6), term='Weekly',
                                notional=1200)

class PaymentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('aunicorndev','aunicorndeveloper@gmail.com', 'errornotfound')
        self.loan =  Loan.objects.create(frequency=3, start_date=datetime.date(2024, 12, 6), term='Weekly',
                                  notional=1200, created_by=self.user)
    def test_payment_creation(self):
        obj = Payment.objects.create(payment_date =  datetime.date(2024,12,13), amount = 400,status= 'Pending',loan = self.loan)
        self.assertEqual(obj.payment_date, datetime.date(2024,12,13))
        self.assertEqual(obj.amount,400.00)
        self.assertEqual(obj.status,'Pending')
        self.assertEqual(obj.loan_id, 1)


    def test_model_validation_payment_date_not_present(self):
        with self.assertRaises(IntegrityError):
            Payment.objects.create(amount = 400,status= 'Pending',loan = self.loan)

    def test_model_validation_amount_not_present(self):
        with self.assertRaises(IntegrityError):
            Payment.objects.create(payment_date=datetime.date(2024,12,13),status='Pending',loan=self.loan)
    def test_model_validation_loan_id_not_present(self):
        with self.assertRaises(IntegrityError):
            Payment.objects.create(payment_date=datetime.date(2024,12,13), amount=400,status='Pending')


class RepaymentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('aunicorndev','aunicorndeveloper@gmail.com', 'errornotfound')
        self.loan =  Loan.objects.create(frequency=3, start_date=datetime.date(2024, 12, 6), term='Weekly',
                                  notional=1200, created_by=self.user)
        self.payment = Payment.objects.create(payment_date =  datetime.date(2024,12,13), amount = 400,status= 'Pending',loan = self.loan)
    def test_repayment_creation(self):
        obj = Repayment.objects.create(amount = 200, payment = self.payment)
        self.assertEqual(obj.amount,200.00)
        self.assertEqual(obj.payment_id, 1)

    def test_model_validation_amount_not_present(self):
        with self.assertRaises(IntegrityError):
            Repayment.objects.create(payment_id=1)
    def test_model_validation_payment_id_not_present(self):
        with self.assertRaises(IntegrityError):
            Repayment.objects.create( amount=200)

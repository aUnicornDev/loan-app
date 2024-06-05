import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from loan.models import Loan,Payment,Repayment,WorkflowStatus
from rest_framework.utils import json


class AuthenticatedUser(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'testuser@example.com', 'testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client.login(username='testuser', password='testpassword')


class AuthenticatedSuperUser(AuthenticatedUser):
    def setUp(self):
        super().setUp()
        self.super_user = User.objects.create_superuser('superuser', 'superuser@example.com', 'superpassword')
        self.super_token = Token.objects.create(user=self.super_user)
        self.super_client = APIClient()
        self.super_client.credentials(HTTP_AUTHORIZATION='Token ' + self.super_token.key)
        self.super_client.login(username='superuser', password='superpassword')


class TestUnAuthenticatedAPIEndpoints(APITestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user('testuser', 'testuser@example.com', 'testpassword')
        Loan.objects.create(frequency=3, start_date=datetime.date(2024, 12, 6), term='Weekly', notional=1200,created_by_id = 1)
        self.loan_payload = {
            "notional": 1000,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "19-03-2024"
        }

    def test_GET_listLoans_whenCalledWithoutAuthentication_shouldReturnUnauthorizedStatus(self):
        response = self.client.get(reverse('loan-list'))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GET_viewLoan_whenCalledWithoutAuthentication_shouldReturnUnauthorizedStatus(self):
        response = self.client.get(reverse('loan-detail',kwargs={"pk":1}))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_POST_addLoan_whenCalledWithoutAuthentication_shouldReturnUnauthorizedStatus(self):
        response = self.client.post(reverse('loan-list'),data=json.dumps(self.loan_payload),content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_POST_approveLoan_whenCalledWithoutAuthentication_shouldReturnUnauthorizedStatus(self):
        response = self.client.patch(reverse('loan-approve',kwargs={"pk":1}))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GET_viewPayment_whenCalledWithoutAuthentication_shouldReturnUnauthorizedStatus(self):
        response = self.client.get(reverse('payment-detail',kwargs={"loan_id":1,"payment_id":1}))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GET_addRepayment_whenCalledWithoutAuthentication_shouldReturnUnauthorizedStatusStatus(self):
        response = self.client.get(reverse('repayment',kwargs={"loan_id":1,'payment_id':1}))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_GET_addPrepayment_whenCalledWithoutAuthentication_shouldReturnUnauthorizedStatus(self):
        response = self.client.get(reverse('prepayment',kwargs={"loan_id":1}))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthenticatedLoanAPIEndpoints(AuthenticatedUser):
    def setUp(self):
        super().setUp()
        self.loan_payload = {
            "notional": 1000,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "19-03-2024"
        }
        self.repayment_payload = {
            "amount": 115
        }

    def test_GET_listLoans_whenCalledWithAuthentication_shouldReturn_OKStatus(self):
        response = self.client.get(reverse('loan-list'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_POST_addLoan_whenCalledWithAuthentication_shouldReturn_OKStatus(self):
        response = self.client.post(reverse('loan-list'),data=json.dumps(self.loan_payload),content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_GET_viewLoan_whenCalledWithAuthentication_shouldReturn_OKStatus(self):
        self.client.post(reverse('loan-list'), data=json.dumps(self.loan_payload),
                                    content_type='application/json')
        response = self.client.get(reverse('loan-detail',kwargs={"pk":1}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_POST_approveLoan_whenCalledWithAuthentication_shouldReturn_ForbiddenStatus(self):
        response = self.client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_GET_viewPayment_whenCalledWithAuthentication_shouldReturn_OKStatus(self):
        self.client.post(reverse('loan-list'), data=json.dumps(self.loan_payload),
                                    content_type='application/json')
        response = self.client.get(reverse('payment-detail', kwargs={"loan_id": 1, "payment_id": 1}))
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class TestSuperUserLoanAPIEndpoints(AuthenticatedSuperUser):
    def setUp(self):
        super().setUp()
        self.loan_payload = {
            "notional": 1000,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "19-03-2024"
        }
        self.repayment_payload = {
            "amount": 115
        }

    def test_POST_approveLoan_whenCalledWithAuthentication_shouldReturn_Accepted(self):
        self.super_client.post(reverse('loan-list'), data=json.dumps(self.loan_payload),
                         content_type='application/json')
        response = self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_POST_addRepayment_whenCalledWithAuthentication_shouldReturn_OKStatus(self):
        self.client.post(reverse('loan-list'), data=json.dumps(self.loan_payload),
                         content_type='application/json')

        response = self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))

        response = self.client.post(reverse('repayment', kwargs={"loan_id": 1, 'payment_id': 1}),
                                    data=json.dumps(self.repayment_payload), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_POST_addPrepayment_whenCalledWithAuthentication_shouldReturn_OKStatus(self):
        response = self.client.post(reverse('loan-list'), data=json.dumps(self.loan_payload),
                                    content_type='application/json')
        self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        response = self.client.post(reverse('prepayment', kwargs={"loan_id": 1}),
                                    data=json.dumps(self.repayment_payload), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


class TestMultiClientAPIEndpoints(AuthenticatedUser):
    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user('testuser2', 'testuser2@example.com', 'testpassword2')
        self.token2 = Token.objects.create(user=self.user2)
        self.loan_payload = {
            "notional": 1000,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "19-03-2024"
        }

        self.loan_payload2 = {
            "notional": 500,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "25-11-2024"
        }

    def test_GET_listLoans_whenCalledFromDifferentUsers_shouldReturnUserSpecificLoans(self):
        self.client.post(reverse('loan-list'), data=json.dumps(self.loan_payload),
                                    content_type='application/json')
        self.client.post(reverse('loan-list'), data=json.dumps(self.loan_payload),
                         content_type='application/json')

        response = self.client.get(reverse('loan-list'))

        self.client.logout()
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        self.client2.login(username='testuser2', password='testpassword2')

        self.client2.post(reverse('loan-list'), data=json.dumps(self.loan_payload2),
                                      content_type='application/json')
        self.client2.post(reverse('loan-list'), data=json.dumps(self.loan_payload2),
                          content_type='application/json')
        self.client2.post(reverse('loan-list'), data=json.dumps(self.loan_payload2),
                          content_type='application/json')
        self.client2.post(reverse('loan-list'), data=json.dumps(self.loan_payload2),
                          content_type='application/json')
        response2 = self.client2.get(reverse('loan-list'))

        self.assertNotEqual(len(response.data), len(response2.data))
        self.assertNotEqual(response.data[0]['id'],response2.data[0]['id'])
        self.assertNotEqual(response.data[0]['notional'], response2.data[0]['notional'])


class TestLoanApprovalAPIEndpoints(AuthenticatedSuperUser):
    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user('testuser2', 'testuser2@example.com', 'testpassword2')
        self.token2 = Token.objects.create(user=self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        self.client2.login(username='testuser2', password='testpassword2')

        self.loan_payload2 = {
            "notional": 500,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "25-11-2024"
        }

        self.client2.post(reverse('loan-list'), data=json.dumps(self.loan_payload2),content_type='application/json')

    def test_GET_viewLoan_whenCreated_shouldHaveStatusAsPending(self):
        response = self.client2.get(reverse('loan-detail', kwargs={"pk": 1}))
        self.assertEquals(response.data['status'],WorkflowStatus.PENDING)

    def test_GET_viewLoan_whenApproved_shouldHaveStatusAsApproved(self):
        self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        response = self.client2.get(reverse('loan-detail', kwargs={"pk": 1}))
        self.assertEquals(response.data['status'], WorkflowStatus.APPROVED)


class TestLoanPaymentAPIEndpoints(AuthenticatedSuperUser):
    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user('testuser2', 'testuser2@example.com', 'testpassword2')
        self.token2 = Token.objects.create(user=self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        self.client2.login(username='testuser2', password='testpassword2')

        self.loan_payload2 = {
            "notional": 500,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "25-11-2024"
        }

        self.repayment_payload = {
            "amount":115
        }
        self.repayment_payload2 = {
            "amount": 26
        }
        self.client2.post(reverse('loan-list'), data=json.dumps(self.loan_payload2), content_type='application/json')

    def test_POST_AddRepayment_whenUnApproved_shouldThrowError(self):
        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1,"payment_id":4}),data=self.repayment_payload)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['non_field_errors'][0],"Cannot add payments. The loan is under approval")

    def test_POST_AddRepayment_whenApproved_shouldCreatePayment(self):
        self.super_client.login(username='superuser', password='superpassword')
        response = self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        self.super_client.logout()

        self.client2.login(username='testuser2', password='testpassword2')
        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1,"payment_id":7}),data=self.repayment_payload)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['outstanding_balance'],0.00)

        response = self.client2.get(reverse('loan-detail',kwargs={'pk':1}))
        self.assertEquals(response.data['payments'][0]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][1]['outstanding_balance'],35.00)
        self.assertEquals(response.data['payments'][2]['outstanding_balance'],50.00)
        self.assertEquals(response.data['payments'][3]['outstanding_balance'],50.00)
        self.assertEquals(response.data['payments'][4]['outstanding_balance'],50.00)
        self.assertEquals(response.data['payments'][5]['outstanding_balance'],50.00)
        self.assertEquals(response.data['payments'][6]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][7]['outstanding_balance'],50.00)
        self.assertEquals(response.data['payments'][8]['outstanding_balance'],50.00)
        self.assertEquals(response.data['payments'][9]['outstanding_balance'],50.00)

        self.assertEquals(response.data['payments'][0]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][1]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][2]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][3]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][4]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][5]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][6]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][7]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][8]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][9]['status'], WorkflowStatus.PENDING)

        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1,"payment_id":8}),data=self.repayment_payload2)

        response = self.client2.get(reverse('loan-detail', kwargs={'pk': 1}))
        self.assertEquals(response.data['payments'][0]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][1]['outstanding_balance'], 35.00)
        self.assertEquals(response.data['payments'][2]['outstanding_balance'], 50.00)
        self.assertEquals(response.data['payments'][3]['outstanding_balance'], 50.00)
        self.assertEquals(response.data['payments'][4]['outstanding_balance'], 50.00)
        self.assertEquals(response.data['payments'][5]['outstanding_balance'], 50.00)
        self.assertEquals(response.data['payments'][6]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][7]['outstanding_balance'], 24.00)
        self.assertEquals(response.data['payments'][8]['outstanding_balance'], 50.00)
        self.assertEquals(response.data['payments'][9]['outstanding_balance'], 50.00)

        self.assertEquals(response.data['payments'][0]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][1]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][2]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][3]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][4]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][5]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][6]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][7]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][8]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][9]['status'], WorkflowStatus.PENDING)

    def test_POST_AddRepayment_whenAddedToPaidStatus_shouldThrowError(self):
        self.super_client.login(username='superuser', password='superpassword')
        response = self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        self.super_client.logout()

        self.client2.login(username='testuser2', password='testpassword2')
        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1,"payment_id":7}),data=self.repayment_payload)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['outstanding_balance'],0.00)

        self.client2.post(reverse('repayment', kwargs={"loan_id": 1,"payment_id":8}),data=self.repayment_payload2)

        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1, "payment_id": 7}),
                                     data=self.repayment_payload2)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['non_field_errors'][0], "Cannot add payments. The payment is already paid.")

        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1, "payment_id": 7}),
                                     data={"amount":400})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['non_field_errors'][0], "Repayment/ Prepayment amount cannot be greater than Outstanding Balance.")

        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1, "payment_id": 8}),
                                     data={"amount": 359})
        response = self.client2.post(reverse('repayment', kwargs={"loan_id": 1, "payment_id": 7}),
                                     data={"amount": 2})

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['non_field_errors'][0],
                          "Cannot add payments. The loan is already paid.")






class TestLoanPrepaymentAPIEndpoints(AuthenticatedSuperUser):
    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user('testuser2', 'testuser2@example.com', 'testpassword2')
        self.token2 = Token.objects.create(user=self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        self.client2.login(username='testuser2', password='testpassword2')

        self.loan_payload2 = {
            "notional": 500,
            "term": "Weekly",
            "frequency": 10,
            "start_date": "25-11-2024"
        }

        self.repayment_payload = {
            "amount":375
        }
        self.repayment_payload2 = {
            "amount": 26
        }

        self.client2.post(reverse('loan-list'), data=json.dumps(self.loan_payload2), content_type='application/json')

    def test_POST_AddPrepayment_whenUnApproved_shouldThrowError(self):
        response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),data=self.repayment_payload)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['non_field_errors'][0],"Cannot add payments. The loan is under approval")

    def test_POST_AddPrepayment_whenApproved_shouldCreatePayment(self):
        self.super_client.login(username='superuser', password='superpassword')
        response = self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        self.super_client.logout()

        self.client2.login(username='testuser2', password='testpassword2')
        response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),data=self.repayment_payload)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        self.assertEquals(response.data['payments'][0]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][1]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][2]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][3]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][4]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][5]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][6]['outstanding_balance'],0.00)
        self.assertEquals(response.data['payments'][7]['outstanding_balance'],25.00)
        self.assertEquals(response.data['payments'][8]['outstanding_balance'],50.00)
        self.assertEquals(response.data['payments'][9]['outstanding_balance'],50.00)

        self.assertEquals(response.data['payments'][0]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][1]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][2]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][3]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][4]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][5]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][6]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][7]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][8]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][9]['status'], WorkflowStatus.PENDING)

        response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),data=self.repayment_payload2)

        self.assertEquals(response.data['payments'][0]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][1]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][2]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][3]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][4]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][5]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][6]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][7]['outstanding_balance'], 0.00)
        self.assertEquals(response.data['payments'][8]['outstanding_balance'], 49.00)
        self.assertEquals(response.data['payments'][9]['outstanding_balance'], 50.00)

        self.assertEquals(response.data['payments'][0]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][1]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][2]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][3]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][4]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][5]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][6]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][7]['status'], WorkflowStatus.PAID)
        self.assertEquals(response.data['payments'][8]['status'], WorkflowStatus.PENDING)
        self.assertEquals(response.data['payments'][9]['status'], WorkflowStatus.PENDING)

        # response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}), data=self.repayment_payload)
        # self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEquals(response.data['non_field_errors'][0], "Repayment/ Prepayment amount cannot be greater than Outstanding Balance.")

    def test_POST_AddPrepayment_whenAddedToPaidStatus_shouldThrowError(self):
        self.super_client.login(username='superuser', password='superpassword')
        response = self.super_client.patch(reverse('loan-approve', kwargs={"pk": 1}))
        self.super_client.logout()

        self.client2.login(username='testuser2', password='testpassword2')
        response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),
                                     data=self.repayment_payload)

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)


        self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),
                          data=self.repayment_payload2)


        response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),
                                     data={"amount": 400})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['non_field_errors'][0],
                          "Repayment/ Prepayment amount cannot be greater than Outstanding Balance.")

        response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),
                                     data={"amount": 99})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.post(reverse('prepayment', kwargs={"loan_id": 1}),
                                     data={"amount": 2})

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.data['non_field_errors'][0],
                          "Cannot add payments. The loan is already paid.")











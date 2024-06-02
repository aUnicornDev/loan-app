from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import LoanSerializer,PaymentSerializer
from ..models import Loan, Payment, WorkflowStatus
from dateutil.relativedelta import *
from dateutil.parser import parse
from rest_framework.authtoken.models import Token

class LoanListView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, *args, **kwargs):
        '''
        List all the loans
        '''
        token = request.auth.key
        user = Token.objects.get(key=token).user_id
        print(user)
        if 'loanSysId' in kwargs:
            id = kwargs.get('loanSysId')
            loan = Loan.objects.get(id = id)
            loan_serializer = LoanSerializer(loan)
        else:
            loan = Loan.objects.all()
            loan_serializer = LoanSerializer(loan, many=True)
        return Response(loan_serializer.data, status=status.HTTP_200_OK)

    def post(self,request):
        '''
        Create loan object and its underlying payment objects
        '''
        notional = request.data.get('notional')
        startDate = request.data.get('startDate')
        term = request.data.get('term')
        frequency = request.data.get('frequency')
        startDate = parse(startDate)

        loan = Loan.objects.create(notional=notional, startDate=startDate.date(), term=term, frequency = frequency)


        amount = notional/frequency
        count = 1
        while count <= frequency:
            paymentDate = startDate + relativedelta(weeks=count)
            Payment.objects.create(loanSysId = loan,paymentDate = paymentDate.date(), amount = amount)
            count+=1

        loan_serializer = LoanSerializer(loan)

        return Response(loan_serializer.data, status=status.HTTP_200_OK)



class LoanApprovalView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request,*args, **kwargs):
        '''
        Create loan object and its underlying payment objects
        '''

        if 'loanSysId' in kwargs:
            id = kwargs.get('loanSysId')
            loan = Loan.objects.get(id = id)
            loan.status = WorkflowStatus.APPROVED
            loan_serializer = LoanSerializer(loan)

        return Response(loan_serializer.data, status=status.HTTP_200_OK)


class PaymentListView(APIView):
    def get(self, request, *args, **kwargs):
        '''
        List all the payments for a loan
        '''

        if 'loanSysId' in kwargs and 'paymentSysId' in kwargs:
            id = kwargs.get('loanSysId')
            paymentId = kwargs.get('paymentSysId')
            payments = Payment.objects.get(id = paymentId, loanSysId_id = id)
            payment_serializer = PaymentSerializer(payments)
        elif 'loanSysId' in kwargs:
            id = kwargs.get('loanSysId')
            payments = Payment.objects.filter( loanSysId_id=id)
            payment_serializer = PaymentSerializer(payments,many=True)
        return Response(payment_serializer.data, status=status.HTTP_200_OK)

    def post(self,request):
        '''
        Create loan object and its underlying payment objects
        '''
        notional = request.data.get('notional')
        startDate = request.data.get('startDate')
        term = request.data.get('term')
        frequency = request.data.get('frequency')
        startDate = parse(startDate)

        loan = Loan.objects.create(notional=notional, startDate=startDate.date(), term=term, frequency = frequency)


        amount = notional/frequency
        count = 1
        while count <= frequency:
            paymentDate = startDate + relativedelta(weeks=count)
            Payment.objects.create(loanSysId = loan,paymentDate = paymentDate.date(), amount = amount)
            count+=1

        loan_serializer = LoanSerializer(loan)

        return Response(loan_serializer.data, status=status.HTTP_200_OK)






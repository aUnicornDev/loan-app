from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import LoanSerializer
from ..models import Loan,Payment
from dateutil.relativedelta import *
from dateutil.parser import parse

class LoanListView(APIView):
    def get(self, request, *args, **kwargs):
        '''
        List all the loans
        '''
        loan = Loan.objects.filter()
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






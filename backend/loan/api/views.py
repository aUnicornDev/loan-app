from django.core.handlers import exception
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import LoanSerializer,PaymentSerializer
from ..models import Loan, Payment, WorkflowStatus,Repayment
from dateutil.relativedelta import *
from dateutil.parser import parse
from rest_framework.authtoken.models import Token
from decimal import Decimal

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
            loan = Loan.objects.filter(createdBy_id = user)
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

        loan = Loan.objects.create(notional=notional, startDate=startDate.date(), term=term, frequency = frequency,createdBy = request.user)

        amount = notional/frequency
        count = 1
        while count <= frequency:
            paymentDate = startDate + relativedelta(weeks=count)
            Payment.objects.create(loanSysId = loan,paymentDate = paymentDate.date(), amount = amount)
            count+=1

        loan_serializer = LoanSerializer(loan)

        return Response(loan_serializer.data, status=status.HTTP_201_CREATED)



class LoanApprovalView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request,*args, **kwargs):
        '''
        Create loan object and its underlying payment objects
        '''

        if 'loanSysId' in kwargs:
            id = kwargs.get('loanSysId')
            loan = Loan.objects.get(id = id)
            #Check if Loan object is already Approved
            loan.status = WorkflowStatus.APPROVED
            loan.save()
            loan_serializer = LoanSerializer(loan)

        return Response(loan_serializer.data, status=status.HTTP_201_CREATED)


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

    def post(self,request,*args, **kwargs):
        '''
        Create loan object and its underlying payment objects
        '''
        if 'loanSysId' in kwargs:

            repayment_amount = round(Decimal(request.data.get('amount')), 6)
            id = kwargs.get('loanSysId')
            if Loan.objects.get(id = id).status != WorkflowStatus.APPROVED:
                return Response("Cannot add payments. The loan is under approval", status=status.HTTP_428_PRECONDITION_REQUIRED)
            if 'paymentSysId' in kwargs:
                payment_id =  kwargs.get('paymentSysId')
                payment = Payment.objects.get(id=payment_id)
                if payment.status == WorkflowStatus.PAID:
                    return Response("Already Paid", status=status.HTTP_200_OK)

                if repayment_amount >= payment.balance_amount:
                    prepayment_amount = repayment_amount - payment.balance_amount
                    Repayment.objects.create(amount=payment.balance_amount, payment_id=payment.id)
                    payment.status = WorkflowStatus.PAID
                    payment.save()

                    if prepayment_amount > 0:
                        payments = Payment.objects.filter(status=WorkflowStatus.PENDING, loanSysId_id=id).order_by(
                            'id')
                        # payment_id = payments[0].id
                        for idx, payment in enumerate(payments):
                            if idx < len(payments) and prepayment_amount > payment.balance_amount:
                                prepayment_amount -= payment.balance_amount
                                Repayment.objects.create(amount=payment.balance_amount, payment_id=payment.id)
                                payment_obj = Payment.objects.get(id=payment.id, loanSysId_id=id)
                                payment_obj.status = WorkflowStatus.PAID
                                payment_obj.save()
                            else:
                                # payment_obj = Payment.objects.get(id=payment.id, loanSysId_id=id)
                                Repayment.objects.create(amount=prepayment_amount, payment_id=payment.id)
                                break

                    # repayment_amount = prepayment_amount

                else:
                    Repayment.objects.create(amount=repayment_amount, payment_id=payment.id)
                payments = Payment.objects.get(id=payment_id, loanSysId_id=id)
                payment_serializer = PaymentSerializer(payments)
                return Response(payment_serializer.data, status=status.HTTP_201_CREATED)

            else:
                prepayment_amount = repayment_amount
                payments = Payment.objects.filter(status=WorkflowStatus.PENDING, loanSysId_id=id).order_by('id')
                for idx, payment in enumerate(payments):
                    if idx < len(payments) and prepayment_amount > payment.balance_amount:
                        prepayment_amount -= payment.balance_amount
                        Repayment.objects.create(amount=payment.balance_amount, payment_id=payment.id)
                        payment_obj = Payment.objects.get(id=payment.id, loanSysId_id=id)
                        payment_obj.status = WorkflowStatus.PAID
                        payment_obj.save()
                    else:
                        # payment_obj = Payment.objects.get(id=payment.id, loanSysId_id=id)
                        Repayment.objects.create(amount=prepayment_amount, payment_id=payment.id)
                        break

                loan = Loan.objects.get(id=id)
                loan_serializer = LoanSerializer(loan)
                return Response(loan_serializer.data, status=status.HTTP_201_CREATED)



        return Response("", status=status.HTTP_200_OK)






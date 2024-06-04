from django.core.handlers import exception
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.viewsets import ModelViewSet

from .serializers import LoanSerializer, PaymentSerializer, RepaymentSerializer
from ..models import Loan, Payment, WorkflowStatus, Repayment


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Loan.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save()

    @action(methods=['patch'], detail=True, permission_classes=[IsAdminUser])
    def approve(self, request, pk):
        loan = Loan.objects.get(id=pk)
        loan.status = WorkflowStatus.APPROVED
        loan.save()
        return Response({'message': 'Loan approved'}, status=status.HTTP_201_CREATED)


class RepaymentViewSet(viewsets.ModelViewSet):
    queryset = Repayment.objects.all()
    serializer_class = RepaymentSerializer

    def create(self, request, loan_id, payment_id=None):

        serializer = RepaymentSerializer(data={'amount': request.data['amount'], 'payment_id': payment_id, 'loan_id': loan_id})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if payment_id is not None:
                payment = Payment.objects.get(id=payment_id)
                return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
            else:
                loan = Loan.objects.get(id=loan_id)
                return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def retrieve(self, request, loan_id, payment_id):
        queryset = self.get_queryset(payment_id)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self, payment_id):
        return Payment.objects.get(id=payment_id)
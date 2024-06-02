from ..models import Loan, Payment

from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id','status','amount','paymentDate']
        model = Payment


class LoanSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source='payment_set')
    class Meta:
        model = Loan
        fields = ['id','status','notional','term','frequency','startDate','payments']

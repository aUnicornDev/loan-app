from ..models import Loan, Payment

from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    class Meta:
        fields = ['status','amount','paymentDate']
        model = Payment


class LoanSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source='payment_set')
    class Meta:
        model = Loan
        fields = ['status','notional','term','frequency','startDate','payments']

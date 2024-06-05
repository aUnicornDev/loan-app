from decimal import Decimal
from dateutil.relativedelta import relativedelta
from ..models import Loan, Payment, Repayment, WorkflowStatus
from rest_framework import serializers

class LoanPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id','status','amount','payment_date','outstanding_balance']
        model = Payment

class LoanSerializer(serializers.ModelSerializer):
    payments = LoanPaymentSerializer(many=True, read_only=True, source='payment_set')
    class Meta:
        model = Loan
        fields = ['id','status','notional', 'term', 'frequency', 'start_date', 'total_cumulative_repayments','payments']
        read_only_fields = ['id', 'total_cumulative_repayments']

    def validate_notional(self,value):
        if value <= 0:
            raise serializers.ValidationError("Notional cannot be negative or 0.")
        return value

    def validate_frequency(self,value):
        if value <= 0:
            raise serializers.ValidationError("Frequency cannot be negative or 0.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        loan = Loan.objects.create(created_by=user, **validated_data)

        notional = Decimal(validated_data['notional'])
        frequency = validated_data['frequency']
        start_date = validated_data['start_date']

        amount = round(Decimal(notional) / frequency,6)
        payment_count = 1
        sum_amount = Decimal(0)
        while payment_count < frequency:
            payment_date = start_date + relativedelta(weeks=payment_count)
            Payment.objects.create(loan = loan,payment_date = payment_date, amount = amount)
            sum_amount+=amount
            payment_count += 1
        payment_date = start_date + relativedelta(weeks=payment_count)
        Payment.objects.create(loan=loan, payment_date=payment_date, amount=notional-sum_amount)
        return loan


class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['created_date','amount']
        model = Repayment

    def validate_amount(self,value):
        if value <= 0:
            raise serializers.ValidationError("Amount cannot be negative or 0.")
        return value

    def validate(self, data):
        amount = data['amount']
        loan_id = self.initial_data['loan_id']
        payment_id = self.initial_data['payment_id']
        loan = Loan.objects.get(id=loan_id)

        if loan.status == WorkflowStatus.PAID:
            raise serializers.ValidationError("Cannot add payments. The loan is already paid.")
        elif loan.status == WorkflowStatus.PENDING:
            raise serializers.ValidationError("Cannot add payments. The loan is under approval")
        if loan.total_outstanding_balance < amount:
            raise serializers.ValidationError("Repayment/ Prepayment amount cannot be greater than Outstanding Balance.")

        if payment_id is not None:
            payment = Payment.objects.get(id=payment_id)
            if payment.status == WorkflowStatus.PAID:
                raise serializers.ValidationError("Cannot add payments. The payment is already paid.")
        return data

    @staticmethod
    def __create__repayment(payment, amount, repayment_list, status=None):
        repayment = Repayment.objects.create(amount=amount, payment=payment)
        repayment_list.append(repayment)
        if status is not None:
            payment.status = status
            payment.save()

    def create(self, validated_data):

        repayment_amount = validated_data['amount']
        payment_id = self.initial_data['payment_id']
        loan_id = self.initial_data['loan_id']

        repayment_list = []

        if payment_id is not None:
            payment = Payment.objects.get(id=payment_id)
            if repayment_amount >= payment.outstanding_balance:
                repayment_amount -= payment.outstanding_balance
                self.__create__repayment(payment,payment.outstanding_balance,repayment_list,WorkflowStatus.PAID)
            else:
                self.__create__repayment(payment, repayment_amount,repayment_list)
                repayment_amount = 0

        if repayment_amount > 0:
            prepayment_amount = repayment_amount
            payments = Payment.objects.filter(status=WorkflowStatus.PENDING, loan_id=loan_id).order_by('id')
            for idx, payment in enumerate(payments):

                if idx < len(payments) and prepayment_amount > payment.outstanding_balance:
                    prepayment_amount -= payment.outstanding_balance
                    self.__create__repayment(payment, payment.outstanding_balance,repayment_list, WorkflowStatus.PAID)

                else:
                    self.__create__repayment(payment, prepayment_amount,repayment_list)
                    break

        loan = Loan.objects.get(id=loan_id)
        if loan.total_cumulative_repayments == loan.notional:
            loan.status = WorkflowStatus.PAID
            loan.save()
        return repayment_list[0]


class PaymentSerializer(serializers.ModelSerializer):
    repayments = RepaymentSerializer(many=True, read_only=True, source='repayment_set')
    class Meta:
        model = Payment
        fields = ['id','status', 'amount', 'payment_date','outstanding_balance','repayments']



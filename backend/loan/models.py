from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class WorkflowStatus(models.TextChoices):
    PENDING = "Pending",_("Pending")
    APPROVED = "Approved",_("Approved")
    PAID = "Paid",_ ("Paid")

class PaymentTerm(models.TextChoices):
    WEEKLY = "Weekly", _("Weekly")

class Loan(models.Model):
    status = models.CharField(max_length=10,choices=WorkflowStatus,default=WorkflowStatus.PENDING)
    notional = models.DecimalField( max_digits=19, decimal_places=6)
    term = models.CharField(max_length=10,choices=PaymentTerm,default=PaymentTerm.WEEKLY)
    start_date = models.DateField()
    frequency = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    @property
    def total_cumulative_repayments(self):
        total = sum(payment.cumulative_repayments for payment in self.payment_set.all())
        return Decimal(total).quantize(Decimal('.1') ** 6)

    @property
    def total_outstanding_balance(self):
        return self.notional - self.total_cumulative_repayments


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment_date = models.DateField()
    status = models.CharField(max_length=10, choices=WorkflowStatus, default=WorkflowStatus.PENDING)
    amount = models.DecimalField( max_digits=19, decimal_places=6)

    @property
    def cumulative_repayments(self):
        total = self.repayment_set.aggregate(total=Sum('amount'))['total']
        return Decimal(total).quantize(Decimal('.1') ** 6) if total is not None else Decimal(0)

    @property
    def outstanding_balance(self):
        return self.amount - self.cumulative_repayments


class Repayment(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=now)
    amount = models.DecimalField( max_digits=19, decimal_places=6)


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
    startDate = models.DateField()
    frequency = models.IntegerField()
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=now)

    @property
    def total_repayed_amount(self):
        total_repayed = sum(payment.repayed_amount for payment in self.payment_set.all())
        return total_repayed



class Payment(models.Model):
    loanSysId = models.ForeignKey(Loan, on_delete=models.CASCADE)
    paymentDate = models.DateField()
    status = models.CharField(max_length=10, choices=WorkflowStatus, default=WorkflowStatus.PENDING)
    amount = models.DecimalField( max_digits=19, decimal_places=6)

    @property
    def repayed_amount(self):
        total = self.repayment_set.aggregate(total=Sum('amount'))['total']
        return total if total is not None else Decimal(0)

    @property
    def balance_amount(self):
        return round(self.amount - self.repayed_amount,6)


class Repayment(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=now)
    amount = models.DecimalField( max_digits=19, decimal_places=6)


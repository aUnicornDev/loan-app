from django.db import models
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


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
    created = models.DateTimeField(db_default=Now(),default=Now())



class Payment(models.Model):
    loanSysId = models.ForeignKey(Loan, on_delete=models.CASCADE)
    paymentDate = models.DateField()
    status = models.CharField(max_length=10, choices=WorkflowStatus, default=WorkflowStatus.PENDING)
    amount = models.DecimalField( max_digits=19, decimal_places=6)

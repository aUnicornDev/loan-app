from django.contrib import admin
from .models import Loan, Payment,Repayment

# Register your models here.
admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(Repayment)

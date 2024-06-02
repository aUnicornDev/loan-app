
from django.urls import path, include
from .views import LoanListView,PaymentListView,LoanApprovalView

urlpatterns = [
    path('', LoanListView.as_view()),
    path('<int:loanSysId>/', LoanListView.as_view()),
    path('<int:loanSysId>/approve', LoanApprovalView.as_view()),
    path('<int:loanSysId>/payment/<int:paymentSysId>', PaymentListView.as_view()),
    path('<int:loanSysId>/payment/', PaymentListView.as_view()),
]
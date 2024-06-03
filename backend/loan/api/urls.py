
from django.urls import path, include
from .views import LoanListView,PaymentListView,LoanApprovalView

urlpatterns = [
    path('', LoanListView.as_view(),name = 'list_loan'),
    path('<int:loanSysId>/', LoanListView.as_view(),name = 'get_loan'),

    path('<int:loanSysId>/approve', LoanApprovalView.as_view(),name = 'approve_loan'),

    path('<int:loanSysId>/payment/<int:paymentSysId>', PaymentListView.as_view()),
    path('<int:loanSysId>/payment/', PaymentListView.as_view()),

    path('<int:loanSysId>/repayment/<int:paymentSysId>', PaymentListView.as_view(),name = 'add_repayment'),
    path('<int:loanSysId>/prepayment/', PaymentListView.as_view(),name = 'add_prepayment'),
]
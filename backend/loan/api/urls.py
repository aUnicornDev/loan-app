from django.urls import path, include
from rest_framework import routers

from .views import PaymentViewSet,LoanViewSet,RepaymentViewSet

router = routers.DefaultRouter()
router.register(r'', LoanViewSet)

urlpatterns = [

    path('', include(router.urls)),
    path('<int:loan_id>/payment/<int:payment_id>/', PaymentViewSet.as_view({'get': 'retrieve'}),name = 'payment-detail'),
    path('<int:loan_id>/repayment/<int:payment_id>/', RepaymentViewSet.as_view({'post': 'create'}),name = 'repayment'),
    path('<int:loan_id>/prepayment/', RepaymentViewSet.as_view({'post': 'create'}),name = 'prepayment')
]
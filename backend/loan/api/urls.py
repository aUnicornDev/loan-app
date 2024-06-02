
from django.urls import path, include
from .views import LoanListView

urlpatterns = [
    path('', LoanListView.as_view()),
]
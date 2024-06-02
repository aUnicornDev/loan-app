from django.urls import path, include
from .views import RegisterView,CustomAuthToken

urlpatterns = [

    path('register/',RegisterView.as_view()),
    path('token/', CustomAuthToken.as_view())
]
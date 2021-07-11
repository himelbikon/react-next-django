from django.urls import path
from .views import *

urlpatterns = [
    path('links/<str:code>', LinkAPIView.as_view()),
    path('orders', OrderAPIView.as_view()),
]

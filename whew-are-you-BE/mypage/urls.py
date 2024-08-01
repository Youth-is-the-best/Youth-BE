from django.urls import path
from .views import *

urlpatterns = [
    path('', MyInfoAPIView.as_view()),    
]

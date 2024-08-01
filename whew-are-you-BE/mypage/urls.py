from django.urls import path
from .views import *

urlpatterns = [
    path('', MyInfoAPIView.as_view()),    
    path('news/', NewsAPIView.as_view())
]

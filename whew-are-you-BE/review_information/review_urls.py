from django.urls import path
from .views import ReviewAPIView

urlpatterns = [
    path('', ReviewAPIView.as_view()),
]

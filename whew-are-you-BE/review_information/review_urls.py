from django.urls import path
from .views import ReviewAPIView, ReviewDetailAPIView

urlpatterns = [
    path('', ReviewAPIView.as_view()),
    path('<int:id>/', ReviewDetailAPIView.as_view()),
]

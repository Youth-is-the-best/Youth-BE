from django.urls import path
from .views import PortfolioAPIView, ThisIsMeAPIView, ThisIsMeDetailAPIView, BingoCompleteAPIView, BingoCompleteDetailAPIView

urlpatterns = [
    path('', PortfolioAPIView.as_view()),
    path('this-is-me/', ThisIsMeAPIView.as_view()),
    path('this-is-me/<int:id>/', ThisIsMeDetailAPIView.as_view()),
    path('bingo-complete/', BingoCompleteAPIView.as_view()),
    path('bingo-complete/<int:id>/', BingoCompleteDetailAPIView.as_view()),
]

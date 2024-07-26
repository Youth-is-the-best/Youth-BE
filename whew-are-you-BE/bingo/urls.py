from django.urls import path
from .views import BingoAPIView

urlpatterns = [
    path('', BingoAPIView.as_view()),    # 빙고 판 설정
]

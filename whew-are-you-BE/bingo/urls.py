from django.urls import path
from .views import *

urlpatterns = [
    path('', BingoAPIView.as_view()),    # 빙고 판 설정
    path('items/<int:item_id>', BingoItemAPIView.as_view())
]

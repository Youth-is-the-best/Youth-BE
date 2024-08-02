from django.urls import path
from .views import *

urlpatterns = [
    path('', BingoAPIView.as_view()),    # 빙고 판 설정
    path('loc/<int:location>/', BingoObjAPIView.as_view()),
    path('review/', BingoReviewAPIView.as_view()),      # 빙고 인증용 후기글
    path('recs/upcoming/', BingoUpcomingAPIView.as_view()),
    path('recs/saved/', BingoSavedAPIView.as_view()),
    path('recs/', BingoRecsAPIView.as_view()), #유형별 추천
    path('items/<int:pk>/', BingoItemAPIView.as_view()),
    path('dday/', DdayAPIView.as_view()),      # 디데이를 설정하거나 가져오기
    path('todo/<int:todo_id>', ToDoAPIView.as_view()) #투두 체크박스 수정용 엔드포인트
]

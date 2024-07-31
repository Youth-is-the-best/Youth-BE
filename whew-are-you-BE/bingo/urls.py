from django.urls import path
from .views import *

urlpatterns = [
    path('', BingoAPIView.as_view()),    # 빙고 판 설정
    path('loc/<int:location>/', BingoObjAPIView.as_view()),
    path('review/', BingoReviewAPIView.as_view()),      # 빙고 인증용 후기글
    path('recs/upcoming/', BingoUpcomingAPIView.as_view()),
    path('recs/saved/', BingoSavedAPIView.as_view()),
    path('recs/', BingoRecsAPIView.as_view()) #유형별 추천
]

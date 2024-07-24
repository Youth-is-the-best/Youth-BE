from django.urls import path
from .views import SubmitAnswerAPIView, QuestionListAPIView, ChoiceListAPIView

urlpatterns = [
    path('submit-answer/', SubmitAnswerAPIView.as_view(), name='submit-answer'),    # 답변 제출
    path('questions/', QuestionListAPIView.as_view(), name='questions-list'),       # 질문 목록
    path('choices/', ChoiceListAPIView.as_view(), name='choices-list'),             # 선지 목록
]

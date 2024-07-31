from django.urls import path
from .views import *

urlpatterns = [
    path('', NoticeAPIView.as_view()),
    path('likes/<int:id>/', NoticeLikeAPIView.as_view()),
    path('storages/<int:id>/', NoticeStorageAPIView.as_view()),
]

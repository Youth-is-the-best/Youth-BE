from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("join/", RegisterView.as_view()),      # 회원가입
    path("login/", RegisterView.as_view()),     # 로그인
]
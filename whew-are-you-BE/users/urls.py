from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("join/", RegisterView.as_view()),      # 회원가입
    path("login/", LoginView.as_view()),        # 로그인
    path("logout/", LogoutView.as_view()),      # 로그아웃
    path("verify/", VerifyMailView.as_view())
]
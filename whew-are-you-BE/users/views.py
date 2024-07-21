from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout

from .serializers import *
from verify_email.email_handler import send_verification_email
from .form import CustomUserForm


# 회원가입 뷰
class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            print(validated_data)
            form = CustomUserForm(validated_data)
            pending_user = send_verification_email(request, form)

            # TODO: 이 아래 로직은 별도의 view로 분리하거나 위의 email 인증을 별도의 뷰로 빼거나 해야함
            if pending_user.is_active is True:
                user = pending_user
                token = RefreshToken.for_user(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
                res = Response(
                    {
                        "user": serializer.data,
                        "message": "register success",
                        "token": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
                return res
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# 로그인 뷰
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            access_token = serializer.validated_data["access_token"]
            refresh_token = serializer.validated_data["refresh_token"]
            res = Response(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                    },
                    "message": "login success",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            res.set_cookie("access-token", access_token, httponly=True)
            res.set_cookie("refresh-token", refresh_token, httponly=True)
            return res
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# 로그아웃 뷰
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "로그아웃되었습니다."}, status=status.HTTP_200_OK)
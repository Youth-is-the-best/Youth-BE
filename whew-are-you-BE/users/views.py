from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout

from .serializers import *
from .sendmail import send_email
import random
from .models import Verif


# 회원가입 뷰
class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
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
    
class VerifyMailView(APIView):
    #이메일 인증을 요청하는 경우
    def post(self, request):
        # TODO: 나중에 아래 검증 로직을 VerifSerializer로 빼기
        email = request.data.get('email')            
        if not email:
            return Response({"error": "이메일 주소가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        #이미 회원으로 가입된 메일 주소인지 확인
        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "이미 가입된 이메일 주소입니다."}, status=status.HTTP_400_BAD_REQUEST)
        #아니라면, 인증번호 생성 후 django.mail을 통해, 인증번호 이메일 발송
        #인증번호 생성
        verif_code = str(random.randint(100000, 999999))
        try:
            new_verif_request = Verif(email, verif_code)
            new_verif_request.save()
            send_email(email, verif_code)
        except:
            return Response({"error": "발송 중 오류가 발생했습니다. 잠시 후 다시 시도 바랍니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"success": "인증번호가 메일로 발송되었습니다."}, status=status.HTTP_200_OK)
    
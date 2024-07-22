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
    
class VerifyMailView(APIView):
    #이메일 인증을 요청하는 경우
    def post(self, request):
        email = request.data.get('email')            
        password = request.data.get('password')
        if not email or not password:
            return Response({"error": "이메일 주소와 비밀번호가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        #이미 회원으로 가입된 메일 주소인지 확인
        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "이미 가입된 이메일 주소입니다."}, status=status.HTTP_400_BAD_REQUEST)
        #아니라면, 링크 생성
        #django.mail을 통해, 생성된 링크 이메일 발송
        #링크를 통해 회원가입 마저 하라고 안내
        pass

    #인증 링크를 누르는 경우
    def get(self, request):
        #해시값이 존재하는지 확인
        #해시 생성 시간 확인, 유효기간 지났으면 X
        #is_active값을 False->True로 변경, 이미 True면 X
        #회원가입을 마저 하기 위한 해시 생성 후 프론트로 리다이렉트

        #추후 프론트는 해시값과 회원가입에 필요한 나머지 값을 RegisterView로 전송하면, CustomUser의 모든 필드 채워진채로 가입 완료
        #우리는 RegisterView와 이떼 사용하는 Serializer만 손보면 됨.
        pass
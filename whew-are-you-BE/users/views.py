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
from django.utils import timezone
from datetime import timedelta
import hashlib
import hmac
import base64
import os, json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json') 

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets): 
# secret 변수를 가져오거나 그렇지 못 하면 예외를 반환
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


# 회원가입 뷰
class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save(request)
            user_serializer = CustomUserSerializer(user)
            user_data = user_serializer.data
            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": user_data,
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
        
    def get(self, request):
        query = request.data.get('username')
        existing = CustomUser.objects.filter(username=query)
        if not query:
            return Response({"error": "username 필드 필요"}, status=status.HTTP_400_BAD_REQUEST)

        existing = CustomUser.objects.filter(username=query)
        if existing.exists():
            return Response({"available": False}, status=status.HTTP_200_OK)
        else:
            return Response({"available": True}, status=status.HTTP_200_OK)
        

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
        request_type = request.data.get('request_type')
        if request_type == "1":
            return self.send_verif_email(request)
        if request_type == "2":
            return self.validate_6code(request)
        else:
            return Response({"error": "유효하지 않은 request_type 파라메터입니다."}, status=status.HTTP_400_BAD_REQUEST)

    def send_verif_email(self, request):
        email = request.data.get('email')            
        if not email:
            return Response({"error": "이메일 주소가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        #이미 회원으로 가입된 메일 주소인지 확인
        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "이미 가입된 이메일 주소입니다.", "short_msg": "email_taken"}, status=status.HTTP_400_BAD_REQUEST)
        #학교 이메일인지 확인
        domain = email.split('@')[1]
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, 'schools.json')

        with open(json_path, 'r', encoding='utf-8') as file:
            school_data = json.load(file)
        school_name = school_data.get(domain)
        if school_name is None :
            school_name = "멋쟁이사자처럼대학"
            pass
            #TODO 실배포시 살리기
            #return Response({"error": "학교 이메일 주소만 가입 가능합니다. ", "short_msg": "notschoolemail"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            school_name = school_name[0]

        #인증번호 생성 후 django.mail을 통해, 인증번호 이메일 발송
        #인증번호 생성
        verif_code = str(random.randint(100000, 999999))
        try:
            #해당 이메일에 대한 모든 이전 요청을 무효화
            prev_verif = Verif.objects.filter(email=email)
            for req in prev_verif:
                req.is_valid = False
                req.save()
            #학교 정보를 넣어 새로운 Verif 만들기    
            new_verif_request = Verif(email=email, verif_code=verif_code, school=school_name)
            new_verif_request.save()
            send_email(email, verif_code)
        except Exception as e:
            print(e)
            return Response({"error": "발송 중 서버 오류가 발생했습니다. 잠시 후 다시 시도 바랍니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if school_name is None :
            return Response({"error": "학교 이메일 주소만 가입 가능합니다. 단 테스트 기간에는 사용 가능합니다. 인증번호는 메일로 발송되었습니다.", "short_msg": "not_school_email"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({f"success": "인증번호가 메일로 발송되었습니다."}, status=status.HTTP_200_OK)
    
    def validate_6code(self, request):
        email = request.data.get('email')
        verif_code = request.data.get('verif_code')            
        if not verif_code:
            return Response({"error": "6자리 인증번호가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        #Verif object 중 email 일치하는 것 고르기
        #timedelta<5분인 것 고르기
        #is_valid=True인 것 고르기
        #verif_code 일치하는 것 고르기
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        #인증번호부터 검증
        verif_objects = Verif.objects.filter(email=email, verif_code=verif_code, is_valid=True)
        if not verif_objects.exists():
            return Response({"error": "유효하지 않은 인증번호입니다.", "short_msg": "invalid_code"}, status=status.HTTP_401_UNAUTHORIZED)
        
        #인증번호 맞더라도 5분 지나면 
        verif_objects = verif_objects.filter(created_at__gte=five_minutes_ago)
        if not verif_objects.exists():
            return Response({"error": "인증번호가 만료되었습니다.", "short_msg": "code_expired"}, status=status.HTTP_401_UNAUTHORIZED)
        
        #무결성 hash값(이메일을 대신) 생성, 저장 
        secret_key = base64.b64decode(get_secret("B64_HMAC_KEY"))
        msg_str = email + str(timezone.now())
        hash = hmac.new(secret_key, msg=msg_str.encode(), digestmod=hashlib.sha256).digest()
        base64_hash = base64.b64encode(hash).decode()

        assert (verif_objects.count() == 1)
        school_name = verif_objects.first().school
        verif_objects.update(is_valid=False, hash=base64_hash, is_fulfilled=True)

        return Response({"success": "인증이 완료되었습니다.", "hash": base64_hash, "school": school_name}, status=status.HTTP_200_OK)


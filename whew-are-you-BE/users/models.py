from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.CharField(max_length=30, unique=True)     #이게 pk가 되어선 안됨.
    email = models.EmailField()
    phone_number = models.CharField(max_length=16)              # 전화번호
    university = models.CharField(max_length=20)                # 대학
    college = models.CharField(max_length=20)                   # 단과대학
    major = models.CharField(max_length=20)                     # 전공
    is_premium = models.BooleanField(default=False)             # 프리미엄 여부
    birth = models.DateField()                                  # 생년월일
    deleted_at = models.DateTimeField(null=True, blank=True)    # 회원 탈퇴 시간
    is_active = models.BooleanField(default=False)

    @staticmethod
    def get_user_or_none_by_username(username):
        try:
            return CustomUser.objects.get(username=username)
        except Exception:
            return None
        
class PendingUser(AbstractUser): #하나의 가입 시도당 1개 생김
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    password = models.CharField(max_length=20)
    link = models.CharField(max_length=50, null=True) #이메일로 전송되는 링크에의 해시
    hash = models.CharField(max_length=50, null=True) #프론트로 리다이렉트 될때 사용되는 해시
    is_active = models.BooleanField(default=True) #이전 가입 시도는 False로 변경
    
    @staticmethod
    def get_pending_or_none_by_username(email):
        try:
            return PendingUser.objects.get(email=email)
        except ObjectDoesNotExist:
            return None
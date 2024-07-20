from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=16)      # 전화번호
    university = models.CharField(max_length=20)        # 대학
    college = models.CharField(max_length=20)           # 단과대학
    major = models.CharField(max_length=20)             # 전공
    is_primium = models.BooleanField(default=False)     # 프리미엄 여부
    birth = models.DateField()                          # 생년월일
    deleted_at = models.DateTimeField(null=True)        # 회원 탈퇴 시간
    email_checked = models.BooleanField(default=False)  # 이메일 인증 여부
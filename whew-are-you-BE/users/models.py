from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.CharField(max_length=30, unique=True)                  #이게 pk가 되어선 안됨.
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
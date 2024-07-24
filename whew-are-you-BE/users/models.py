from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.CharField(max_length=30, unique=True)     #이게 pk가 되어선 안됨.
    email = models.EmailField()
    university = models.CharField(max_length=20)                # 대학
    college = models.CharField(max_length=20, null=True)                   # 단과대학
    major = models.CharField(max_length=20, null=True)                     # 전공
    is_premium = models.BooleanField(default=False)             # 프리미엄 여부
    deleted_at = models.DateTimeField(null=True, blank=True)    # 회원 탈퇴 시간
    is_active = models.BooleanField(default=False)

    @staticmethod
    def get_user_or_none_by_username(username):
        try:
            return CustomUser.objects.get(username=username)
        except Exception:
            return None
        
class Verif(models.Model): #하나의 인증요청당 1개 생김
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    verif_code = models.CharField(max_length=6)
    hash = models.CharField(max_length=45, null=True) #최종회원가입시 프->백으로 이 해시를 넘겨줘야 함.
    is_valid = models.BooleanField(default=True) #인증시간 초과된 것과 별개로, 여러개의 인증요청 올 경우, 최신 번호만 남겨두고 나머지는 비활성화
    is_fulfilled = models.BooleanField(default=False) #인증이 완료되면 hash값이 생기고 is_fulfilled=True로 바뀜

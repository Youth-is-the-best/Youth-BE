from django.db import models
from django.conf import settings

# 빙고 판 모델
class Bingo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)     # 빙고판의 사용자
    size = models.IntegerField(default=9)       # 빙고의 크기(9, 16)
    start_date = models.DateField()     # 빙고 시작 날짜
    end_date = models.DateField()       # 빙고 종료 날짜
    is_active = models.BooleanField(default=True)       # 빙고 활성화 여부(end_date 이후로는 False가 됨)
    change_chance = models.IntegerChoices(default=3)        # 빙고 수정 남은 기회
from django.db import models
from django.conf import settings
from users.models import CustomUser


# 일단 임시로 만들어 두기
class Review(models.Model):
    title = models.CharField(max_length=50)


# 빙고 항목 베이스 모델
class BaseBingoItem(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    BINGO_CATEGORIES = [
        ('CAREER', '채용'),
        ('CERTIFICATE', '자격증'),
        ('OUTBOUND', '대외활동'),
        ('CONTEST', '공모전'),
        ('SELFCARE', '취미/여행/자기계발/휴식'),
    ]
    title = models.CharField(max_length=50)
    large_category = models.CharField(max_length=20, choices=BINGO_CATEGORIES)
    small_category = models.CharField(max_length=20, null=True, blank=True)
    duty = models.CharField(max_length=50, null=True) #직무
    employment_form = models.CharField(max_length=50, null=True) #채용형태
    area = models.CharField(max_length=50, null=True) #근무/활동지역
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    host = models.CharField(max_length=50, null=True) 
    app_fee = models.IntegerField(null=True)
    prep_period = models.IntegerField(null=True)
    app_due = models.DateField(null=True)
    field = models.CharField(max_length=20, null=True)
    image = models.ImageField(null=True)

    class Meta:
        abstract = True

class ProvidedBingoItem(BaseBingoItem):
    type = models.ForeignKey('typetest.Type', on_delete=models.SET_NULL, null=True)
    is_editable = models.BooleanField(default=False)

class CustomBingoItem(BaseBingoItem):
    is_editable = models.BooleanField(default=True)


# 빙고 판 모델
class Bingo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)     # 빙고판의 사용자
    size = models.IntegerField(default=9)       # 빙고의 크기(9, 16)
    start_date = models.DateField()     # 빙고 시작 날짜
    end_date = models.DateField()       # 빙고 종료 날짜
    is_active = models.BooleanField(default=True)       # 빙고 활성화 여부(end_date 이후로는 False가 됨)
    change_chance = models.IntegerField(default=3)        # 빙고 수정 남은 기회


# 빙고 칸 모델
class BingoSpace(models.Model):
    bingo = models.ForeignKey(Bingo, on_delete=models.CASCADE)      # 빙고
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)        # 사용자
    is_executed = models.BooleanField(default=False)        # 실행 완료 여부
    start_date = models.DateField()     # 항목 시작 날짜
    end_date = models.DateField()       # 항목 종료 날짜
    image = models.ImageField(null=True, blank=True)        # 나중에 후기글의 대표 이미지
    recommend_content = models.ForeignKey(ProvidedBingoItem, null=True, blank=True, on_delete=models.CASCADE)        # 추천 항목
    self_content = models.ForeignKey(CustomBingoItem, null=True, blank=True, on_delete=models.CASCADE)     # 직접 입력 항목
    review = models.ForeignKey(Review, null=True, blank=True, on_delete=models.CASCADE)       # 후기글
    location = models.IntegerField()    # 빙고 칸 위치


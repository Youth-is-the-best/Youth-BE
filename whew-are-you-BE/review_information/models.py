from django.db import models
from bingo.models import BingoSpace, ToDo
from users.models import CustomUser

# 후기글 모델
class Review(models.Model):

    BINGO_CATEGORIES = [
        ('CAREER', '채용'),
        ('CERTIFICATE', '자격증'),
        ('OUTBOUND', '대외활동'),
        ('CONTEST', '공모전'),
        ('HOBBY', '취미'),
        ('TRAVEL', '여행'),
        ('SELFIMPROVEMENT', '자기계발'),
        ('REST', '휴식')
    ]

    bingo_space = models.OneToOneField(BingoSpace, null=True, blank=True, related_name='review', on_delete=models.CASCADE)      # 빙고 인증용 후기글이면 빙고칸과 연결
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review', blank=True, null=True)
    title = models.CharField(max_length=50)
    large_category = models.CharField(max_length=20, choices=BINGO_CATEGORIES)
    todo = models.OneToOneField(ToDo, on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    content = models.TextField()
    duty = models.CharField(max_length=50, null=True)       #직무
    employment_form = models.CharField(max_length=50, null=True)        #채용형태
    area = models.CharField(max_length=50, null=True)       #근무/활동지역
    work_period = models.IntegerField(blank=True, null=True)        # 근무 기간
    host = models.CharField(max_length=50, null=True) # 주최사
    app_fee = models.IntegerField(null=True)    # 응시료
    prep_period = models.IntegerField(null=True)        # 총 준비 기간
    app_due = models.DateField(null=True)       # 지원 마감일
    field = models.CharField(max_length=20, null=True)      # 공모 분야


# 후기글 이미지
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_images')
    image = models.ImageField(upload_to='review/')


# 정보글 모델
class Information(models.Model):
    BINGO_CATEGORIES = [
        ('CAREER', '채용'),
        ('CERTIFICATE', '자격증'),
        ('OUTBOUND', '대외활동'),
        ('CONTEST', '공모전'),
        ('HOBBY', '취미'),
        ('TRAVEL', '여행'),
        ('SELFIMPROVEMENT', '자기계발'),
        ('REST', '휴식')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='information', blank=True, null=True)
    title = models.CharField(max_length=50)
    large_category = models.CharField(max_length=20, choices=BINGO_CATEGORIES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    content = models.TextField()


# 정보글 이미지
class InformationImage(models.Model):
    information = models.ForeignKey(Information, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='information/')
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

    bingo_space = models.OneToOneField(BingoSpace, null=True, blank=True, related_name='review')      # 빙고 인증용 후기글이면 빙고칸과 연결
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review')
    title = models.CharField(max_length=50)
    large_category = models.CharField(max_length=20, choices=BINGO_CATEGORIES)
    todo = models.OneToOneField(ToDo)
    start_date = models.DateField()
    end_date = models.DateField()
    content = models.TextField()


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

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='information')
    title = models.CharField(max_length=50)
    large_category = models.CharField(max_length=20, choices=BINGO_CATEGORIES)
    start_date = models.DateField()
    end_date = models.DateField()
    content = models.TextField()


# 정보글 이미지
class InformationImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='information_images')
    image = models.ImageField(upload_to='information/')
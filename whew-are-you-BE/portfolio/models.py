from django.db import models
from users.models import CustomUser

# 포트폴리오 모델
class Portfolio(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='portfolio')
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    birth = models.DateField(blank=True, null=True)
    school_major = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


# 저는 이런 사람입니다(?) 모델
class ThisIsMe(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='this_is_me')
    content = models.TextField()


# 달성한 빙고
class BingoComplete(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='bingo_complete')
    content = models.TextField()


# 다른 성과
class OtherComplete(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='other_complete')
    content = models.TextField()
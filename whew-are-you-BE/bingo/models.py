from django.db import models
from users.models import CustomUser

# Create your models here.
class BaseBingoItem(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    large_category = models.

    BINGO_CATEGORIES = [
        ('CAREER', '채용'),
        ('CERTIFICATE', '자격증'),
        ('PANDA', '대외활동'),
        ('BEAVER', '공모전'),
        ('EAGLE', '취미/여행/자기계발/휴식'),
    ]
    user_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    class Meta:
        abstract = True
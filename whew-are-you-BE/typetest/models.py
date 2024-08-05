from django.db import models
from django.conf import settings

# 질문 모델
class Question(models.Model):
    # 질문의 번호는 id와 같음(primary key)
    content = models.TextField()


# 질문 선지 모델
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=50)


# 사용자 답변 모델
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    answer_text = models.TextField(null=True, blank=True)
    return_year = models.IntegerField(null=True, blank=True)
    return_semester = models.IntegerField(null=True, blank=True)


# 타입(7가지) 모델
class Type(models.Model):
    TYPE_CHOICES = [
        ('SQUIRREL', '다람쥐'),
        ('RABBIT', '토끼'),
        ('PANDA', '판다'),
        ('BEAVER', '비버'),
        ('EAGLE', '독수리'),
        ('BEAR', '곰'),
        ('DOLPHIN', '돌고래'),
    ]
    user_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='typetest/')
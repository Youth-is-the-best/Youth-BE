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
        ('CHALLENGER', '도전가'),
        ('ACTIVIST', '활동가'),
        ('RESTER', '휴식가'),
        ('LEARNER', '학습가'),
        ('TRAVELER', '여행자'),
        ('STRATEGIST', '전략가'),
        ('EXPLORER', '탐험가'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
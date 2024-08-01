from django.db import models
from users.models import CustomUser
from review_information.models import Review, Information

# 알림창 모델
class News(models.Model):
    user = models.OneToOneField(CustomUser)     # 사용자
    heart = models.BooleanField(default=True)       # 공감 알림 설정
    comment = models.BooleanField(default=True)     # 댓글 알림 설정
    point = models.BooleanField(default=True)       # 포인트 알림 설정
    hue = models.BooleanField(default=True)         # 휴알유 포스트 알림 추천

    CATEGORIES = [
        ('HEART', '하트'),
        ('POINT', '포인트'),
        ('COMMENT', '댓글'),
        ('PROMOTE', '홍보')
    ]
    category = models.CharField(max_length=20, choices=CATEGORIES)      # 알림의 종류
    content = models.CharField(max_length=50)       # 알림의 내용 ~님이 댓글을 남겼습니다.
    small_content = models.TextField(blank=True, null=True)     # 세부 내용
    is_clicked = models.BooleanField(default=False)     # 클릭된 알림인지

    review = models.ForeignKey(Review, blank=True, null=True, related_name='news')       # 알림에 연결된 후기글
    information = models.ForeignKey(Information, blank=True, null=True, related_name='news')         # 알림에 연결된 정보글

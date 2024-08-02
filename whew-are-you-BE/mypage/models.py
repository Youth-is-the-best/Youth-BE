from django.db import models
from users.models import CustomUser
from review_information.models import Review, Information

# 알림창 모델
class News(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)     # 사용자
    created_at = models.DateTimeField(auto_now_add=True)        # 알림 생성 시간
    created_at_day = models.DateTimeField(auto_now_add=True)        # 알림 생성 날짜

    CATEGORIES = [
        ('HEART', '하트'),
        ('POINT', '포인트'),
        ('COMMENT', '댓글'),
        ('PROMOTE', '홍보')
    ]
    category = models.CharField(max_length=20, choices=CATEGORIES)      # 알림의 종류
    who = models.CharField(max_length=30, blank=True, null=True)        # 누가
    where = models.CharField(max_length=50, blank=True, null=True)      # 어디에
    content = models.CharField(max_length=50, blank=True, null=True)       # 큰 내용
    small_content = models.TextField(blank=True, null=True)     # 세부 내용
    is_clicked = models.BooleanField(default=False)     # 클릭된 알림인지

    review = models.ForeignKey(Review, on_delete=models.CASCADE, blank=True, null=True, related_name='news')       # 알림에 연결된 후기글
    information = models.ForeignKey(Information, on_delete=models.CASCADE, blank=True, null=True, related_name='news')         # 알림에 연결된 정보글


# 설정 모델
class NewsOption(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    heart = models.BooleanField(default=True)       # 공감 알림 설정
    comment = models.BooleanField(default=True)     # 댓글 알림 설정
    point = models.BooleanField(default=True)       # 포인트 알림 설정
    hue = models.BooleanField(default=True)         # 휴알유 포스트 알림 추천
    not_read = models.BooleanField(default=True)    # 안 읽음 기능 설정
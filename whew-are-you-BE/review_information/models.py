from django.db import models
from bingo.models import BingoSpace, ToDo
from users.models import CustomUser

# 후기글 모델
"""
후기글 모델은 크게 [빙고 인증용 후기글], [일반 후기글] 두 가지로 분류할 수 있다.
그리고, 대분류 카테고리에 따라 필요한 필드는 아래와 같다.

1. CAREER(채용, 인턴)
- user: 사용자
- title: 제목
- large_category: 대분류(CAREER)
- duty: 직무
- employment_form: 채용 형태
- area: 근무 지역
- start_date: 근무 시작 날짜
- end_date: 근무 종료 날짜
- procedure: 모집 절차
- content: 준비 과정/합격 팁/소감
- images(이미지)
+) todo(인증용 후기글), bingo_space(인증용 후기글), detailplans(일반 후기글)

2. CERTIFICATE(자격증)
- user: 사용자
- title: 제목
- large_category: 대분류(CERTIFICATE)
- host: 주최사
- app_fee: 응시료
- date: 시험 날짜
- start_date: 준비 시작 날짜
- end_date: 준비 종료 날짜
- procedure: 시험 절차
- content: 준비 과정/공부 팁/소감
- images(이미지)
+) todo(인증용 후기글), bingo_space(인증용 후기글), detailplans(일반 후기글)

3. CONTEST(공모전)
- user: 사용자
- title: 제목
- large_category: 대분류(CONTEST)
- host: 주최 기관
- field: 공모 분야
- app_due: 마감일
- start_date: 준비 시작 날짜
- end_date: 준비 종료 날짜
- content: 준비 과정/수상 팁/소감
- images(이미지)
+) todo(인증용 후기글), bingo_space(인증용 후기글), detailplans(일반 후기글)

4. OUTBOUND(대외활동)
- user: 사용자
- title: 제목
- large_category: 대분류(OUTBOUND)
- field: 활동 분야
- area: 활동 지역
- start_date: 활동 시작 날짜
- end_date: 활동 종료 날짜
- procedure: 모집 절차
- content: 활동 내용/합격 팁/소감
- images(이미지)
+) todo(인증용 후기글), bingo_space(인증용 후기글), detailplans(일반 후기글)

5. 그 외
- user: 사용자
- title: 제목
- large_category: 대분류
- start_date: 활동 시작 날짜
- end_date: 활동 종료 날짜
- content: 소감
- images(이미지)
+) todo(인증용 후기글), bingo_space(인증용 후기글), detailplans(일반 후기글)
"""

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

    # 모든 후기글 양식 공통
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='review')
    title = models.CharField(max_length=50)
    large_category = models.CharField(max_length=20, choices=BINGO_CATEGORIES)
    start_date = models.DateField()
    end_date = models.DateField()
    content = models.TextField()

    # 빙고 인증용 후기글 공통
    bingo_space = models.OneToOneField(BingoSpace, null=True, blank=True, related_name='review', on_delete=models.CASCADE)      # 빙고 인증용 후기글

    # 분류에 따라 달라지는 양식
    duty = models.CharField(max_length=50, null=True)       # 채용: 직무
    employment_form = models.CharField(max_length=50, null=True)        # 채용: 채용 형태
    area = models.CharField(max_length=50, null=True)       # 대외활동, 채용: 근무/활동지역
    host = models.CharField(max_length=50, null=True) # 자격증, 공모전: 주최사, 주최 기관
    app_fee = models.IntegerField(blank=True, null=True)    # 자격증: 응시료
    date = models.DateField(blank=True, null=True)        # 자격증: 시험 날짜
    app_due = models.DateField(null=True)       # 공모전: 마감일
    field = models.CharField(max_length=20, null=True)      # 대외 활동, 공모전: 활동/공모 분야
    procedure = models.TextField(blank=True, null=True)     # 채용, 자격증, 대외활동: 모집 절차, 시험 절차

    # 좋아요, 보관함
    likes = models.ManyToManyField(CustomUser, related_name='like_review', blank=True)
    storage = models.ManyToManyField(CustomUser, related_name='storage_review', blank=True)


# 후기글 이미지
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review/')


# 세부 항목 모델
class DetailPlan(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='detailplans')
    content = models.CharField(max_length=50)


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

    # 좋아요, 보관함
    likes = models.ManyToManyField(CustomUser, related_name='like_information', blank=True)
    storage = models.ManyToManyField(CustomUser, related_name='storage_information', blank=True)


# 정보글 이미지
class InformationImage(models.Model):
    information = models.ForeignKey(Information, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='information/')


# 댓글
class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='author')        # 사용자
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')        # 후기글
    content = models.TextField()        # 댓글 내용
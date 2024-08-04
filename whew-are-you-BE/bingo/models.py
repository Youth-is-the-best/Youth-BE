from django.db import models
from django.conf import settings
from users.models import CustomUser


# 빙고 항목 베이스 모델
class BaseBingoItem(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
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
    title = models.CharField(max_length=50)
    large_category = models.CharField(max_length=20, choices=BINGO_CATEGORIES)
    small_category = models.CharField(max_length=20, null=True, blank=True)
    duty = models.CharField(max_length=50, null=True) #직무
    employment_form = models.CharField(max_length=50, null=True) #채용형태
    area = models.CharField(max_length=50, null=True) #근무/활동지역
    start_date = models.DateField(null=True) #이건 빙고시작/종료일자가 아니라 진짜 행사 날짜임.
    end_date = models.DateField(null=True)
    host = models.CharField(max_length=50, null=True)   # 자격증: 주최, 공모전: 주최
    app_fee = models.IntegerField(null=True)
    prep_period = models.CharField(max_length=10, null=True)        # 자격증: 준비 기간, 공모전: 준비 기간
    app_due = models.DateField(null=True)       # 채용: 지원마감, 자격증: 다음 시험, 대외 활동: 지원마감
    field = models.CharField(max_length=20, null=True)      # 대외활동: 활동 분야
    image = models.ImageField(null=True)

    class Meta:
        abstract = True

class ProvidedBingoItem(BaseBingoItem):
    type = models.ForeignKey('typetest.Type', on_delete=models.SET_NULL, null=True)
    is_editable = models.BooleanField(default=False)
    is_notice = models.BooleanField(default=False)      # 공고 인지

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
    date = models.DateField(blank=True, null=True)      # 시험 날짜...
    start_date = models.DateField(null=True)     # 항목 시작 날짜
    end_date = models.DateField(null=True)       # 항목 종료 날짜
    image = models.ImageField(null=True, blank=True)        # 나중에 후기글의 대표 이미지
    recommend_content = models.ForeignKey(ProvidedBingoItem, null=True, blank=True, on_delete=models.CASCADE)        # 추천 항목
    self_content = models.ForeignKey(CustomBingoItem, null=True, blank=True, on_delete=models.CASCADE)     # 직접 입력 항목
    location = models.IntegerField()    # 빙고 칸 위치


# 빙고 투두 항목
class ToDo(models.Model):
    title = models.CharField(max_length=50)
    is_completed = models.BooleanField(default=False)
    bingo = models.ForeignKey(Bingo, on_delete=models.CASCADE)
    bingo_space = models.ForeignKey(BingoSpace, on_delete=models.CASCADE, related_name='todo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  


# 공고 
class Notice(models.Model):
    provided_bingo_item = models.OneToOneField(ProvidedBingoItem, on_delete=models.CASCADE, related_name='notice')        # 1:1 연결
    content = models.TextField()        # 설명글
    likes = models.ManyToManyField(CustomUser, related_name='like_notice', blank=True)
    storage = models.ManyToManyField(CustomUser, related_name='storage_notice', blank=True)
    image = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def likes_count(self):
        return self.likes.count()
    
    def comments_count(self):
        return self.comments.count()
    

# 공고 댓글
class Comment(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')        # 사용자
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='comments')        # 공고
    content = models.TextField()        # 댓글 내용
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)     # 대댓글
    created_at = models.DateTimeField(auto_now_add=True)


# 디데이 모델
class Dday(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='dday')
    rest_school = models.DateField(blank=True, null=True)       # 휴학 날짜
    return_school = models.DateField(blank=True, null=True)     # 복학 날짜
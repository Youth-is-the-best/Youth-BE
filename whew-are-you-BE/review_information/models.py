from django.db import models
from bingo.models import BingoSpace

# 일단 임시로 만들어 두기
class Review(models.Model):
    bingo_space = models.OneToOneField(BingoSpace, null=True, blank=True)      # 빙고 인증용 후기글이면 빙고칸과 연결
    title = models.CharField(max_length=50)
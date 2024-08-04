from rest_framework import serializers
from .models import Bingo, BingoSpace, CustomBingoItem, ProvidedBingoItem, ToDo, Notice, Dday, Comment
from review_information.models import ReviewImage, Review
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from datetime import datetime

class CustomDateField(serializers.DateField):
    def to_representation(self, value):
        # 출력 형식 설정
        return value.strftime('%Y.%m.%d')

    def to_internal_value(self, data):
        # 입력 형식 설정
        for date_format in ('%Y.%m.%d', '%Y-%m-%d'):
            try:
                return datetime.strptime(data, date_format).date()
            except ValueError:
                continue
        raise serializers.ValidationError("Invalid date format. Use 'YYYY.MM.DD' or 'YYYY-MM-DD'.")
    

class BingoSpaceSerializer(serializers.ModelSerializer):
    start_date = CustomDateField()
    end_date = CustomDateField()
    date = CustomDateField()

    class Meta: 
        model = BingoSpace
        fields = "__all__"

class CustomBingoItemSerializer(serializers.ModelSerializer):
    start_date = CustomDateField()
    end_date = CustomDateField()

    class Meta:
        model = CustomBingoItem
        fields = "__all__"

class ProvidedBingoItemSerializer(serializers.ModelSerializer):
    large_category_display = serializers.SerializerMethodField()
    start_date = CustomDateField()
    end_date = CustomDateField()
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = ProvidedBingoItem
        fields = "__all__"

    def get_large_category_display(self, obj):
        return obj.get_large_category_display()

class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = "__all__"


# 공고 시리얼라이저
class NoticeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Notice
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        provided_origin = instance.provided_bingo_item
        provided_origin_serializer = ProvidedBingoItemSerializer(provided_origin).data 
        for key, value in provided_origin_serializer.items():
            if key != 'id':
                rep[key] = value
        return rep
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


# 후기글 작성 시리얼라이저
class ReviewPOSTSerializer(serializers.ModelSerializer):
    space_location = serializers.CharField(write_only=True)

    class Meta:
        model = Review
        fields = ["space_location", "procedure", "content", "large_category"]

    def create(self, validated_data):
        # 사용자가 입력
        large_category = validated_data['large_category']       # 분류
        location = int(validated_data.pop('space_location'))      # 빙고 칸의 위치(0~8)
        content = validated_data['content']
        procedure = validated_data.get('procedure')     # 채용, 자격증, 대외 활동: 모집/시험 절차
        images = self.context['request'].FILES.getlist('images')        # 사용자가 올린 이미지

        # 자동 입력
        user = self.context['request'].user
        bingo = Bingo.objects.get(user=user, is_active=True)
        bingo_space = BingoSpace.objects.get(bingo=bingo, location=location)
        todo = bingo_space.todo.all()
        date = bingo_space.date     # 자격증: 시험 날짜
        start_date_user = bingo_space.start_date
        end_date_user = bingo_space.end_date

        # 끌어오기 항목의 후기글인 경우
        if bingo_space.recommend_content:
            title = bingo_space.recommend_content.title         # 제목
            duty = bingo_space.recommend_content.duty       # 채용: 직무
            employment_form = bingo_space.recommend_content.employment_form     # 채용: 채용 형태
            area = bingo_space.recommend_content.area       # 채용: 근무 지역, 대외활동: 활동 지역
            start_date = bingo_space.recommend_content.start_date       # 행사 시작 날짜
            end_date = bingo_space.recommend_content.end_date       # 행사 종료 날짜
            host = bingo_space.recommend_content.host       # 자격증, 공모전: 주최 기관
            app_fee = bingo_space.recommend_content.app_fee     # 자격증: 응시료
            prep_period = bingo_space.recommend_content.prep_period     # 준비 기간
            app_due = bingo_space.recommend_content.app_due         # 공모전: 마감일
            field = bingo_space.recommend_content.field     # 공모전, 대외활동: 분야

        # 직접 작성한 항목의 후기글인 경우
        elif bingo_space.self_content:
            title = bingo_space.self_content.title
            duty = bingo_space.self_content.duty
            employment_form = bingo_space.self_content.employment_form
            area = bingo_space.self_content.area
            start_date = bingo_space.self_content.start_date
            end_date = bingo_space.self_content.end_date
            host = bingo_space.self_content.host
            app_fee = bingo_space.self_content.app_fee
            prep_period = bingo_space.self_content.prep_period
            app_due = bingo_space.self_content.app_due
            field = bingo_space.self_content.field

        # 인턴(채용) 카테고리인 경우
        if large_category == 'CAREER':
            if not procedure:
                raise ValidationError("모집 절차 항목을 입력 해주세요.")
            review = Review(user=user, large_category=large_category, content=content, title=title, start_date=start_date_user, end_date=end_date_user,
                            duty=duty, employment_form=employment_form, area=area, procedure=procedure, bingo_space=bingo_space)
        # 자격증 카테고리인 경우
        elif large_category == 'CERTIFICATE':
            if not procedure:
                raise ValidationError("시험 절차 항목을 입력 해주세요.")
            review = Review(user=user, title=title, large_category=large_category, host=host, app_fee=app_fee, date=date, bingo_space=bingo_space,
                            start_date=start_date_user, end_date=end_date_user, procedure=procedure, content=content)
        # 대외 활동 카테고리인 경우
        elif large_category == 'OUTBOUND':
            if not procedure:
                raise ValidationError("모집 절차 항목을 입력 해주세요.")
            review = Review(user=user, title=title, large_category=large_category, field=field, area=area, start_date=start_date_user, end_date=end_date_user,
                            procedure=procedure, content=content, bingo_space=bingo_space)
        # 공모전 카테고리인 경우
        elif large_category == 'CONTEST':
            review = Review(user=user, title=title, large_category=large_category, host=host, field=field, 
                            app_due=app_due, start_date=start_date_user, end_date=end_date_user, content=content, bingo_space=bingo_space)
        # 그 외(취미, 여행, 자기 계발, 휴식)
        elif large_category in ['HOBBY', 'TRAVEL', 'SELFIMPROVEMENT', 'REST']:
            review = Review(user=user, title=title, large_category=large_category, start_date=start_date_user, end_date=end_date_user, 
                            content=content, bingo_space=bingo_space)
        # 잘못 입력
        else:
            return Response({"error": "요청한 카테고리 항목이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        review.save()

        bingo_space.is_executed = True      # 빙고 완료 표시
        bingo_space.save()

        for image in images:
            image_data = ReviewImage(review=review, image=image)
            image_data.save()
        validated_data['images'] = images
        
        return review
    

# 디데이 시리얼라이저
class DdaySerializer(serializers.ModelSerializer):
    rest_school = CustomDateField()
    return_school = CustomDateField()
    
    class Meta:
        model = Dday
        fields = ['rest_school', 'return_school']


# 공고 댓글 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):

    author_name = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    user_type = serializers.CharField(source='author.type_result.user_type', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'parent', 'author', 'created_at', 'replies', 'author_name', 'user_type']
        read_only_fields = ['id', 'created_at', 'author', 'replies', 'replies', 'author_name', 'user_type']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
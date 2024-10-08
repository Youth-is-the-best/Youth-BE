from rest_framework import serializers
from .models import Information, InformationImage, Review, ReviewImage, DetailPlan, Comment
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from bingo.models import ToDo
from bingo.serializers import ToDoSerializer


# 커스텀 데이트 필드
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


# 정보글 이미지 시리얼라이저
class InformationImageSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField(source='id')

    class Meta:
        model = InformationImage
        fields = ['image_id', 'image']


# 정보글 GET 시리얼라이저
class InformationGETSerializer(serializers.ModelSerializer):
    information_id = serializers.IntegerField(source='id')
    images = InformationImageSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.DateField(read_only=True)

    class Meta:
        model = Information
        fields = ['information_id', 'title', 'content', 'large_category', 'images', 'username', 'created_at']

    def to_representation(self, instance):
        rep =  super().to_representation(instance)
        rep['large_category_display'] = '휴알유' #휴알유 포스트이므로
        return rep

# 정보글 POST 시리얼라이저
class InformationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Information
        fields = ['id', 'title', 'content', 'large_category']

    def create(self, validated_data):
        title = validated_data['title']
        content = validated_data['content']
        large_category = validated_data['large_category']
        images = self.context['request'].FILES.getlist('images')

        information = Information(title=title, content=content, large_category=large_category)
        information.save()
        for image in images:
            image_data = InformationImage(information=information, image=image)
            image_data.save()
        validated_data['images'] = images
        return validated_data
    
    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.large_category = validated_data.get('large_category', instance.large_category)
        instance.save()

        if images_data is not None:
            # Clear existing images if any
            instance.images.all().delete()
            for image_data in images_data:
                InformationImage.objects.create(information=instance, image=image_data)

        return instance
    

# 세부 계획 시리얼라이저
class DetailPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailPlan
        fields = ['content']


# 후기글 이미지 시리얼라이저
class ReviewImageSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField(source='id')

    class Meta:
        model = InformationImage
        fields = ['image_id', 'image']


# 후기글 POST, GET 시리얼라이저
class ReviewSerializer(serializers.ModelSerializer):
    
    detailplans = DetailPlanSerializer(many=True)
    id = serializers.ReadOnlyField()
    start_date = CustomDateField(required=False)
    end_date = CustomDateField(required=False)
    date = CustomDateField(required=False)

    class Meta:
        model = Review
        fields = ['id', 'title', 'large_category', 'detailplans', 'start_date', 'end_date', 'content', 'duty', 'employment_form', 'area', 
                  'host', 'app_fee', 'date', 'app_due', 'field', 'procedure']
    
    def create(self, validated_data):
        # 필수 항목들
        user = self.context['request'].user
        large_category = validated_data['large_category']
        content = validated_data['content']
        title = validated_data['title']
        detailplans = validated_data['detailplans']

        # 필수 항목이 아니니까 get으로 받음
        procedure = validated_data.get('procedure')
        duty = validated_data.get('duty')
        employment_form = validated_data.get('employment_form')
        area = validated_data.get('area')
        host = validated_data.get('host')
        app_fee = validated_data.get('app_fee')
        app_due = validated_data.get('app_due')
        field = validated_data.get('field')
        date = validated_data.get('date')
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        # 인턴(채용) 카테고리인 경우
        if large_category == 'CAREER':
            review = Review(user=user, large_category=large_category, content=content, title=title, start_date=start_date, end_date=end_date,
                            duty=duty, employment_form=employment_form, area=area, procedure=procedure)
        # 자격증 카테고리인 경우
        elif large_category == 'CERTIFICATE':
            review = Review(user=user, title=title, large_category=large_category, host=host, app_fee=app_fee, date=date,
                            start_date=start_date, end_date=end_date, procedure=procedure, content=content)
        # 대외 활동 카테고리인 경우
        elif large_category == 'OUTBOUND':
            review = Review(user=user, title=title, large_category=large_category, field=field, area=area, start_date=start_date, end_date=end_date,
                            procedure=procedure, content=content)
        # 공모전 카테고리인 경우
        elif large_category == 'CONTEST':
            review = Review(user=user, title=title, large_category=large_category, host=host, field=field, app_due=app_due, start_date=start_date, end_date=end_date, content=content)
        # 그 외(취미, 여행, 자기 계발, 휴식)
        elif large_category in ['HOBBY', 'TRAVEL', 'SELFIMPROVEMENT', 'REST']:
            review = Review(user=user, title=title, large_category=large_category, start_date=start_date, end_date=end_date, content=content)
        # 잘못 입력
        else:
            return Response({"error": "요청한 카테고리 항목이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        review.save()
        
        for detailplan in detailplans:
            DetailPlan.objects.create(review=review, **detailplan)
        
        return review
    
    def update(self, instance, validated_data):
        # 필수 항목들 업데이트
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.large_category = validated_data.get('large_category', instance.large_category)

        # 선택 항목 업데이트
        instance.procedure = validated_data.get('procedure', instance.procedure)
        instance.duty = validated_data.get('duty', instance.duty)
        instance.employment_form = validated_data.get('employment_form', instance.employment_form)
        instance.area = validated_data.get('area', instance.area)
        instance.host = validated_data.get('host', instance.host)
        instance.app_fee = validated_data.get('app_fee', instance.app_fee)
        instance.app_due = validated_data.get('app_due', instance.app_due)
        instance.field = validated_data.get('field', instance.field)
        instance.date = validated_data.get('date', instance.date)

        # 리뷰 저장
        instance.save()

        # DetailPlans 업데이트
        detailplans_data = validated_data.get('detailplans')
        if detailplans_data:
            # 기존 DetailPlan 객체들을 삭제하지 않고, 새로 생성된 객체들로 교체합니다.
            instance.detailplans.all().delete()
            for detailplan_data in detailplans_data:
                DetailPlan.objects.create(review=instance, **detailplan_data)

        return instance

# 후기글 GET 시리얼라이저
class ReviewGETSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    detailplans = DetailPlanSerializer(many=True)
    large_category_display = serializers.SerializerMethodField()
    author_id = serializers.IntegerField(source='user.id', read_only=True)
    author = serializers.CharField(source='user.username', read_only=True)
    profile = serializers.CharField(source='user.type_result.user_type', read_only=True)
    created_at = serializers.DateField(read_only=True)
    start_date = CustomDateField()
    end_date = CustomDateField()
    date = CustomDateField()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    todo = serializers.SerializerMethodField(read_only=True) #인증용 후기글이 아니면 null, 인증용 후기글인데 비어있으면 []
    provided_bingo_item = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'title', 'large_category', 'start_date', 'end_date', 'content', 'duty', 'employment_form', 'area', 
                  'host', 'app_fee', 'date', 'app_due', 'field', 'procedure', 'images', 'detailplans', 'likes', 'large_category_display',
                  'author_id', 'author', 'created_at', 'profile', 'likes_count', 'comments_count', 'is_liked_by_user', 'storage', 'todo', 'provided_bingo_item']
        
    def get_large_category_display(self, obj):
        return obj.get_large_category_display()
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_todo(self, obj):
        if obj.bingo_space: # bingo_space가 존재 = 즉 obj가 인증용 후기글이다.
            todo = ToDo.objects.filter(bingo_space=obj.bingo_space)
            todo_serialized = ToDoSerializer(todo, many=True)
            return todo_serialized.data
        else:
            return None #인증용 후기글이 아니면 null, 인증용 후기글인데 비어있으면 []
        
    def get_provided_bingo_item(self, obj):
        if obj.bingo_space and obj.bingo_space.recommend_content:
            return obj.bingo_space.recommend_content.id
        else:
            return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.id in rep['storage']:
            rep['saved'] = True
        else:
            rep['saved'] = False
        return rep

# 댓글 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):

    author_name = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    created_at = serializers.DateField(read_only=True)
    user_type = serializers.ImageField(source='author.type_result.image', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'parent', 'author', 'created_at', 'replies', 'author_name', 'user_type', 'created_at']
        read_only_fields = ['id', 'created_at', 'author', 'replies', 'replies', 'author_name', 'user_type', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

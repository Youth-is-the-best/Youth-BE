from rest_framework import serializers
from .models import Information, InformationImage, Review, ReviewImage, DetailPlan
from rest_framework import status
from rest_framework.response import Response


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

    class Meta:
        model = Information
        fields = ['information_id', 'title', 'content', 'large_category', 'images']


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


# 후기글 POST 시리얼라이저
class ReviewPOSTSerializer(serializers.ModelSerializer):
    
    detailplans = DetailPlanSerializer(many=True)
    id = serializers.ReadOnlyField()

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
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
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
    

# 후기글 GET 시리얼라이저
class ReviewGETSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    detailplans = DetailPlanSerializer(many=True)

    class Meta:
        model = Review
        fields = ['id', 'title', 'large_category', 'start_date', 'end_date', 'content', 'duty', 'employment_form', 'area', 
                  'host', 'app_fee', 'date', 'app_due', 'field', 'procedure', 'images', 'detailplans']
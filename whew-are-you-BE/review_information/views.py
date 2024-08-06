from rest_framework.views import APIView
from .permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Information, InformationImage, Review, ReviewImage
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
import json
from django.db.models import Count
from rest_framework import filters
from django.db.models import Q
from bingo.serializers import NoticeSerializer, ProvidedBingoItemSerializer
from bingo.models import ProvidedBingoItem, Notice
from mypage.models import News
from copy import copy


# 모든 정보글 뷰
class InformationAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    # permission_classes = [IsAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        images = request.FILES
        print(request.FILES)
        serializer = InformationSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        information = Information.objects.all()
        serializer = InformationGETSerializer(information, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 선택 정보글 뷰
class InformationDetailAPIView(APIView):
    def get(self, request, id, *args, **kwargs):
        information = get_object_or_404(Information, id=id)
        serializer = InformationGETSerializer(information)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 일반 후기글 뷰
class ReviewAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        json_data = request.data.get('json')
        if json_data:
            data = json.loads(json_data)
        else:
            data = {}

        serializer = ReviewSerializer(data=data, context={'request':request})
        
        if serializer.is_valid():
            review = serializer.save()
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image in images:
                    ReviewImage.objects.create(review=review, image=image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        large_category = request.query_params.get('large_category', None)
        search_query = request.query_params.get('search', None)
        area = request.query_params.get('area', None)
        field = request.query_params.get('field', None)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        date_limit = datetime(2024, 8, 6) #시간대 UTC+9 기준인지 확인하기!
        reviews = Review.objects.filter(created_at__lte=date_limit)

        if large_category:
            reviews = reviews.filter(large_category=large_category)

        if search_query:
            reviews = reviews.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

        if area:
            reviews = reviews.filter(area=area)

        if field:
            reviews = reviews.filter(field=field)

        if start_date and end_date:
            reviews = reviews.filter(Q(start_date__lte=end_date) & Q(end_date__gte=start_date))
        elif start_date:
            reviews = reviews.filter(Q(start_date__gte=start_date))
        elif end_date:
            reviews = reviews.filter(Q(end_date__lte=end_date))
    
        serializer = ReviewGETSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 후기글 디테일 뷰
class ReviewDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id, *args, **kwargs):
        review = get_object_or_404(Review, id=id)
        serializer = ReviewGETSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id, *args, **kwargs):
        review = get_object_or_404(Review, id=id)

        json_data = request.data.get('json')
        if json_data:
            data = json.loads(json_data)
        else:
            data = {}

        serializer = ReviewSerializer(review, data=data, context={'request':request})

        if serializer.is_valid():
            review = serializer.save()
            if 'images' in request.FILES:
                review.images.all().delete()
                images = request.FILES.getlist('images')
                for image in images:
                    ReviewImage.objects.create(review=review, image=image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id):
        review = get_object_or_404(Review, id=id)
        review.delete()
        return Response({
            "message": "후기글이 성공적으로 삭제되었습니다."
        },status=status.HTTP_204_NO_CONTENT)
    

# 좋아요
class ReviewLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        review = get_object_or_404(Review, id=id)
        if request.user in review.likes.all():
            review.likes.remove(request.user)

            return Response({'message': '좋아요가 취소되었습니다.'})
        
        else:
            review.likes.add(request.user)

            # 후기글의 작성자에게 알림을 생성
            if request.user != review.user:
                who = request.user.username
                where = review.title
                content = who + '님이 [' + where + '] 글에 좋아요를 눌렀습니다.' 
                news = News.objects.create(user=review.user, category='HEART', who=who, where=where, content=content, review=review)

            return Response({'message': '좋아요가 반영되었습니다.'})
        

# 보관함
class ReviewStorageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        review = get_object_or_404(Review, id=id)
        if request.user in review.storage.all():
            review.storage.remove(request.user)
            return Response({'message': '보관함 항목에서 제거되었습니다.'})
        else:
            review.storage.add(request.user)
            return Response({'message': '보관함 항목에 추가되었습니다.'})
        

# 댓글 뷰
class CommentAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, review_id, *args, **kwargs):
        comments = Comment.objects.filter(review_id=review_id, parent__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, review_id, *args, **kwargs):
        review = Review.objects.get(id=review_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, review=review)

            # 후기글의 작성자에게 알림을 생성
            if request.user != review.user:
                who = request.user.username
                where = review.title
                content = who + '님이 [' + where + '] 글에 댓글을 남겼습니다.' 
                small_content = serializer.data['content']
                news = News.objects.create(user=review.user, category='COMMENT', who=who, where=where, content=content, small_content=small_content, review=review)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def delete(self, request, comment_id, *args, **kwargs):
        try:
            comment = Comment.objects.get(id=comment_id)
        except:
            return Response({"error": "댓글이 존재하지 않습니다."})
        
        if request.user == comment.author:
            comment.delete()
            return Response({"message": "댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)

    
    def get(self, request, review_id, format=None):
        review = Review.objects.get(id=review_id)
        comments = Comment.objects.filter(review=review)

        response_data = []

        for comment in comments:
            json = {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.id,
                'review': comment.review.id,
                'user_type': comment.author.type_result.user_type
            }

            response_data.append(json)
        return Response(response_data)

        
class FetchRelatedReviewsAPIView(APIView):

    def get(self, request, bingo_item_id, *args, **kwargs):
        date_limit = datetime(2024, 8, 6) #시간대 UTC+9 기준인지 확인하기!

        bingo_item = ProvidedBingoItem.objects.get(id=bingo_item_id)
        related_reviews = Review.objects.filter(bingo_space__recommend_content_id = bingo_item, created_at__lte=date_limit)
        annotated_reviews = related_reviews.annotate(num_likes=Count('likes'))
        top_reviews = annotated_reviews.order_by('-num_likes') 
        top_reviews = top_reviews[:3]       
        related_serializer = ReviewGETSerializer(top_reviews, many=True).data

        return Response({"success": "연관 후기 3개", "data": related_serializer}, status=status.HTTP_200_OK)
    

# 공고, 후기 전체 검색 뷰
class SearchAPIView(APIView):
    def get(self, request, *args, **kwargs):

        # 응답할 json
        response = {}

        # 공고인 ProvidedBingoItem을 모두 가져오기
        provided_bingo_items = ProvidedBingoItem.objects.filter(is_notice=True)

        large_category = request.query_params.get('large_category', None)
        search_query = request.query_params.get('search', None)
        area = request.query_params.get('area', None)
        field = request.query_params.get('field', None)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if large_category:
            provided_bingo_items = provided_bingo_items.filter(large_category=large_category)

        if area:
            provided_bingo_items = provided_bingo_items.filter(area=area)

        if field:
            provided_bingo_items = provided_bingo_items.filter(field=field)

        if search_query:
            provided_bingo_items = provided_bingo_items.filter(Q(title__icontains=search_query) | Q(notice__content__icontains=search_query))

        if start_date and end_date:
            provided_bingo_items = provided_bingo_items.filter(Q(start_date__lte=end_date) & Q(end_date__gte=start_date))
        elif start_date:
            provided_bingo_items = provided_bingo_items.filter(Q(start_date__gte=start_date))
        elif end_date:
            provided_bingo_items = provided_bingo_items.filter(Q(end_date__lte=end_date))

        # 반환할 데이터를 담음
        data = []
        
        for item in provided_bingo_items:
            try:
                notice_data = Notice.objects.get(provided_bingo_item=item)
                notice_serializer = NoticeSerializer(notice_data, context={'request': request})
                notice = copy(notice_serializer.data)
                data.append(notice)
            except Notice.DoesNotExist:
                # Notice가 존재하지 않을 경우 처리
                continue

        # 공고 글 데이터 담기
        response['notice'] = data

        date_limit = datetime(2024, 8, 6) #시간대 UTC+9 기준인지 확인하기!
        reviews = Review.objects.filter(created_at__lte=date_limit)

        if large_category:
            reviews = reviews.filter(large_category=large_category)

        if search_query:
            reviews = reviews.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

        if area:
            reviews = reviews.filter(area=area)

        if field:
            reviews = reviews.filter(field=field)
        
        if start_date and end_date:
            reviews = reviews.filter(Q(start_date__lte=end_date) & Q(end_date__gte=start_date))
        elif start_date:
            reviews = reviews.filter(Q(start_date__gte=start_date))
        elif end_date:
            reviews = reviews.filter(Q(end_date__lte=end_date))
    
        serializer = ReviewGETSerializer(reviews, many=True, context={'request': request})

        response['review'] = serializer.data

        return Response(response, status=status.HTTP_200_OK)



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
from rest_framework import filters
from django.db.models import Q
from bingo.serializers import NoticeSerializer, ProvidedBingoItemSerializer
from bingo.models import ProvidedBingoItem, Notice


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

        if large_category:
            reviews = Review.objects.filter(large_category=large_category)
        else:
            reviews = Review.objects.all()

        if search_query:
            reviews = reviews.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
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
    
    def post(self, request, review_id, *args, **kwargs):
        review = Review.objects.get(id=review_id)
        serializer = CommentSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save(review=review, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
    

# 공고, 후기 전체 검색 뷰
class SearchAPIView(APIView):
    def get(self, request, *args, **kwargs):

        # 응답할 json
        response = {}

        # 공고인 ProvidedBingoItem을 모두 가져오기
        provided_bingo_items = ProvidedBingoItem.objects.filter(is_notice=True)

        large_category = request.query_params.get('large_category', None)
        search_query = request.query_params.get('search', None)

        if large_category:
            provided_bingo_items = provided_bingo_items.filter(large_category=large_category)

        if search_query:
            provided_bingo_items = provided_bingo_items.filter(Q(title__icontains=search_query) | Q(notice__content__icontains=search_query))

        # 반환할 데이터를 담음
        data = []
        
        for item in provided_bingo_items:
            item_serializer = ProvidedBingoItemSerializer(item)
            notice_data = Notice.objects.get(provided_bingo_item=item)
            notice_serializer = NoticeSerializer(notice_data)

            json_data = {}
            json_data['bingo_item'] = item_serializer.data
            json_data['notice_information'] = notice_serializer.data

            data.append(json_data)

        # 공고 글 데이터 담기
        response['notice'] = data

        if large_category:
            reviews = Review.objects.filter(large_category=large_category)
        else:
            reviews = Review.objects.all()

        if search_query:
            reviews = reviews.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
        serializer = ReviewGETSerializer(reviews, many=True)

        response['review'] = serializer.data

        return Response(response, status=status.HTTP_200_OK)
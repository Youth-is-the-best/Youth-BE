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

        if not large_category:
            review = Review.objects.all()
        else:
            review = Review.objects.filter(large_category=large_category)
        serializer = ReviewGETSerializer(review, many=True)
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

    def get(self, request, review_id, *args, **kwargs):
        comments = Comment.objects.filter(review_id=review_id, parent__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, review_id, *args, **kwargs):
        review = Review.objects.get(id=review_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, review=review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        comment_id = kwargs.get('pk')
        comment = Comment.objects.get(pk=comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        comment_id = kwargs.get('pk')
        comment = Comment.objects.get(pk=comment_id)
        if request.user == comment.author:
            serializer = CommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        comment_id = kwargs.get('pk')
        comment = Comment.objects.get(pk=comment_id)
        if request.user == comment.author:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
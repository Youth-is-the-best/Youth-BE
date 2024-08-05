from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import News
from .serializers import NewsSerializer
from .models import News, NewsOption


class MyInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        name = logged_in_user.first_name
        username = logged_in_user.username
        type_result = logged_in_user.type_result.user_type
        email = logged_in_user.email
        points = "1000"        

        if type_result == 'SQUIRREL':
            type_result = '준비성 철저한 다람쥐'
        elif type_result == 'RABBIT':
            type_result = '열정 가득 부지런한 토끼'
        elif type_result == 'PANDA':
            type_result = '재충전을 원하는 판다'
        elif type_result == 'BEAVER':
            type_result = '끝없는 발전을 추구하는 비버'
        elif type_result == 'EAGLE':
            type_result = '모험을 갈망하는 독수리'
        elif type_result == 'BEAR':
            type_result = '안정을 추구하는 곰'
        elif type_result == 'DOLPHIN':
            type_result = '호기심 많은 돌고래'

        return Response({
            "name": name,
            "username": username,
            "type_result": type_result,
            "email": email,
            "points": points
        }, status=status.HTTP_200_OK)
    

# 알림창 API
class NewsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            option = NewsOption.objects.get(user=user)
        except NewsOption.DoesNotExist:
            option = NewsOption.objects.create(user=user)

        news = News.objects.filter(user=user)

        if not option.heart:
            news = news.exclude(category='HEART')
        if not option.comment:
            news = news.exclude(category='COMMENT')
        if not option.point:
            news = news.exclude(category='POINT')
        if not option.hue:
            news = news.exclude(category='PROMOTE')
        if option.not_read:
            news = news.exclude(is_clicked=True)

        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 공감 알림창 설정 API
class HeartOptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            option = NewsOption.objects.get(user=user)
        except NewsOption.DoesNotExist:
            option = NewsOption.objects.create(user=user)

        if option.heart:
            option.heart = False
            option.save()
            return Response({'message': '공감 알림이 뜨지 않도록 설정되었습니다.'})
        else:
            option.heart = True
            option.save()
            return Response({"message": "공감 알림이 설정되었습니다."})


# 안 읽음 알림창 설정 API
class ReadOptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            option = NewsOption.objects.get(user=user)
        except NewsOption.DoesNotExist:
            option = NewsOption.objects.create(user=user)

        if option.not_read:
            option.not_read = False
            option.save()
            return Response({'message': '안 읽음 설정이 해제되었습니다.'})
        else:
            option.not_read = True
            option.save()
            return Response({"message": "안 읽음 설정이 설정되었습니다."})
        

# 댓글 알림창 설정 API
class CommentOptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            option = NewsOption.objects.get(user=user)
        except NewsOption.DoesNotExist:
            option = NewsOption.objects.create(user=user)

        if option.comment:
            option.comment = False
            option.save()
            return Response({'message': '댓글 알림이 뜨지 않도록 설정되었습니다.'})
        else:
            option.comment = True
            option.save()
            return Response({"message": "댓글 알림이 설정되었습니다."})
        

# 포인트 알림창 설정 API
class PointOptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            option = NewsOption.objects.get(user=user)
        except NewsOption.DoesNotExist:
            option = NewsOption.objects.create(user=user)

        if option.point:
            option.point = False
            option.save()
            return Response({'message': '포인트 알림이 뜨지 않도록 설정되었습니다.'})
        else:
            option.point = True
            option.save()
            return Response({"message": "포인트 알림이 설정되었습니다."})
        

# 휴알유 알림창 설정 API
class HueOptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            option = NewsOption.objects.get(user=user)
        except NewsOption.DoesNotExist:
            option = NewsOption.objects.create(user=user)

        if option.hue:
            option.hue = False
            option.save()
            return Response({'message': '휴알유 정보글 알림이 뜨지 않도록 설정되었습니다.'})
        else:
            option.hue = True
            option.save()
            return Response({"message": "휴알유 정보글 알림이 설정되었습니다."})
        

# 알림 누르면 바로 가기 뷰
class BaroAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        user = request.user
        try:
            news = News.objects.get(id=id)
        except NewsOption.DoesNotExist:
            return Response({"error": "해당하는 id의 알림이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        news.is_clicked = True
        news.save()
        return Response({
            "review": news.review.id
        })
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import News
from .serializers import NewsSerializer


class MyInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        name = logged_in_user.first_name
        username = logged_in_user.username
        type_result = logged_in_user.type_result.user_type
        email = logged_in_user.email
        points = "1000"        

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
        news = News.objects.filter(user=user)
        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
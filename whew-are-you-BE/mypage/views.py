from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework import status


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
    
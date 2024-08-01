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

        return Response({
            "name": name,
            "username": username,
            "type_result": type_result,
            "email": email,
            "points": points
        }, status=status.HTTP_200_OK)
    
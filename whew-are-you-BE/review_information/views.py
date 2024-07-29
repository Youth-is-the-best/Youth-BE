from rest_framework.views import APIView
from .permissions import IsAdminOrReadOnly
from .models import Information, InformationImage
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

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
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ReviewPOSTSerializer(data=request.data, context={'request':request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


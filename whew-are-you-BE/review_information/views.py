from rest_framework.views import APIView
from .permissions import IsAdminOrReadOnly
from .models import Information, InformationImage
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
class InformationAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        serializer = InformationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        information = Information.objects.all()
        serializer = InformationSerializer(information, many=True)
        return Response(serializer.data)
from .serializers import PortfolioSerializer, ThisIsMeSerializer, BingoCompleteSerializer, OtherCompleteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio


# 포트폴리오 뷰
class PortfolioAPIView(APIView):

    # 기본 정보 입력
    def post(self, request, *args, **kwargs):
        serializer = PortfolioSerializer(data=request.data)
        image = request.FILES.get('image')

        if serializer.is_valid():
            serializer.save(user=request.user, image=image)
            return Response({
                "data": serializer.data,
                "message": "포트폴리오 생성 완료"
            }, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 기본 정보 수정
    def put(self, request, *args, **kwargs):
        image = request.FILES.get('image')
        user = request.user
        
        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return Response({"error": "포트폴리오가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PortfolioSerializer(portfolio, data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user, image=image)
            return Response({
                "data": serializer.data,
                "message": "포트폴리오 수정 완료"
            }, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 포트폴리오 가져오기
    def get(self, request, *args, **kwargs):
        response = {}
        user = request.user
        response['username'] = user.username
        
        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return Response({"error": "포트폴리오가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 포트폴리오 기본 정보
        portfolio_serializer = PortfolioSerializer(portfolio)
        response['basic_information'] = portfolio_serializer.data

        # 저는 이런 사람입니다
        this_is_me_serializer = ThisIsMeSerializer(portfolio.this_is_me.all(), many=True)
        response['this_is_me'] = this_is_me_serializer.data

        # 완료 빙고
        bingo_complete_serializer = BingoCompleteSerializer(portfolio.bingo_complete.all(), many=True)
        response['bingo_complete'] = bingo_complete_serializer.data

        # 완료 그 외 한 일
        other_complete_serializer = OtherCompleteSerializer(portfolio.other_complete.all(), many=True)
        response['other_complete'] = other_complete_serializer.data

        return Response(response, status=status.HTTP_200_OK)
from .serializers import PortfolioSerializer, ThisIsMeSerializer, BingoCompleteSerializer, OtherCompleteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio, ThisIsMe, BingoComplete, OtherComplete
from review_information.models import Review, ReviewImage
from review_information.serializers import ReviewGETSerializer
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date


# 포트폴리오 뷰
class PortfolioAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
            portfolio = Portfolio.objects.create(user=user)
        
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
    

# 저는 이런 사람입니다 작성 뷰
class ThisIsMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ThisIsMeSerializer(data=request.data)
        user = request.user

        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return Response({"error": "포트폴리오가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response({
                "data": serializer.data,
                "message": "나는 이런 사람입니다 추가 완료"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 저는 이런 사람입니다 삭제 뷰
class ThisIsMeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        
        try:
            this_is_me = ThisIsMe.objects.get(id=id)
        except ThisIsMe.DoesNotExist:
            return Response({"error": "항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        this_is_me.delete()
        return Response({
            "message": "항목이 성공적으로 삭제되었습니다."
        },status=status.HTTP_204_NO_CONTENT)
    

# 달성한 빙고 작성 뷰
class BingoCompleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BingoCompleteSerializer(data=request.data)
        user = request.user

        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return Response({"error": "포트폴리오가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response({
                "data": serializer.data,
                "message": "달성한 빙고 추가 완료"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 저는 이런 사람입니다 삭제 뷰
class BingoCompleteDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        
        try:
            target = BingoComplete.objects.get(id=id)
        except BingoComplete.DoesNotExist:
            return Response({"error": "항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        target.delete()
        return Response({
            "message": "항목이 성공적으로 삭제되었습니다."
        },status=status.HTTP_204_NO_CONTENT)
    

# 다른 성과 작성 뷰
class OtherCompleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OtherCompleteSerializer(data=request.data)
        user = request.user

        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return Response({"error": "포트폴리오가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response({
                "data": serializer.data,
                "message": "다른 성과 추가 완료"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 다른 성과 삭제 뷰
class OtherCompleteDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        
        try:
            target = OtherComplete.objects.get(id=id)
        except OtherComplete.DoesNotExist:
            return Response({"error": "항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        target.delete()
        return Response({
            "message": "항목이 성공적으로 삭제되었습니다."
        },status=status.HTTP_204_NO_CONTENT)
    

# 사용자의 후기 글 가져오기
class UserReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        only = request.query_params.get('only')

        # 사용자에 대한 모든 후기글 기본 쿼리셋 설정
        reviews = Review.objects.filter(user=user)

        # 기간 설정이 있는 경우 필터링
        if start_date or end_date:
            start_date = parse_date(start_date) if start_date else None
            end_date = parse_date(end_date) if end_date else None

            if start_date and end_date:
                reviews = reviews.filter(Q(start_date__lte=end_date) & Q(end_date__gte=start_date))
            elif start_date:
                reviews = reviews.filter(Q(start_date__gte=start_date))
            elif end_date:
                reviews = reviews.filter(Q(end_date__lte=end_date))

        # 빙고 후기글만 가져오기
        if only == 'bingo':
            reviews = reviews.exclude(bingo_space__isnull=True)

        serializer = ReviewGETSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
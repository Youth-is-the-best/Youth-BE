from rest_framework.views import APIView
from users.models import CustomUser
from .models import Bingo, BingoSpace, ProvidedBingoItem, CustomBingoItem
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# 빙고 저장 & 불러오기
class BingoView(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 빙고의 첫 생성
    def post(self, request, *args, **kwargs):
        user = request.user
        size = request.data.get('size')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        bingo_obj = request.data.get('bingo_obj')

        if size != 9 or size != 16:
            return Response({'error': 'size field should be 9 or 16'}, status=status.HTTP_400_BAD_REQUEST)
        
        Bingo.objects.create(user=user, size=size, start_date=start_date, end_date=end_date)
        bingo = Bingo.objects.get(user=user, is_active=True)

        for index, item in enumerate(bingo_obj):
            choice = item.get('choice')     # 직접 입력 항목이면 "0", 끌어온 항목이면 "1"
            item_id = item.get('id')
            item_id = int(item_id)      # item_id를 정수 처리
            title = item.get('title')

            # null이 아닌 경우
            if item:
                if not choice:      # choice 입력하지 않으면 에러
                    return Response({'error': 'choice field is required'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 직접 입력한 항목의 경우
                if choice == "0":
                    BingoSpace.objects.create(user=user, bingo=bingo, title=title, location=index)
                # 끌어온 항목의 경우
                elif choice == "1":
                    recommend_content = ProvidedBingoItem.objects.get(id=item_id)
                    BingoSpace.objects.create(user=user, bingo=bingo, recommend_content=recommend_content, location=index)
                # 잘못된 choice 형식의 경우
                else:
                    return Response({'error': 'choice field should be 0 or 1'}, status=status.HTTP_400_BAD_REQUEST)
                
            # null인 경우
            if not item:
                BingoSpace.objects.create(user=user, bingo=bingo, location=index)
        
        return Response({
            'message': 'bingo set up success',
            'user': user.username,
            'change_chance': bingo.change_chance
        }, status=status.HTTP_200_OK)
    

    # 빙고 판 정보 불러오기
    def get(self, request, *args, **kwargs):
        user = request.user
        bingo = Bingo.objects.get(user=user, is_active=True)

        if not bingo:
            return Response({'error': 'No active bingo found'}, status=status.HTTP_404_NOT_FOUND)
        
        bingo_spaces = BingoSpace.objects.filter(user=user).order_by('location')
        bingo_obj = []
        
        for item in bingo_spaces:
            if item.recommend_content:
                bingo_obj.append({
                    "choice": "1",
                    "id": str(item.recommend_content.id),
                    "title": item.recommend_content.title
                })
            elif item.self_content:
                bingo_obj.append({
                    "choice": "0",
                    "id": str(item.recommend_content.id),
                    "title": item.recommend_content.title
                })
            else:
                bingo_obj.append(None)
            
        return Response({
            "username": user.username,
            "usertype": user.type_result.user_type,
            "start_date": bingo.start_date,
            "end_date": bingo.end_date,
            "size": bingo.size,
            "bingo_obj": bingo_obj
        }, status=status.HTTP_200_OK)
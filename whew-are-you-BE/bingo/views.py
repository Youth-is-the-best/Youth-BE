from rest_framework.views import APIView
from rest_framework import generics
from users.models import CustomUser
from .models import Bingo, BingoSpace, ProvidedBingoItem, CustomBingoItem
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .serializers import BingoItemSerializer
from users.permissions import IsAuthor


# 빙고 저장 & 불러오기
class BingoAPIView(APIView):
    
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
                    self_content = CustomBingoItem.objects.create(user=user, title=title)
                    BingoSpace.objects.create(user=user, bingo=bingo, title=title, self_content=self_content, location=index)
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
        
        bingo_spaces = BingoSpace.objects.filter(bingo=bingo).order_by('location')
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
                    "id": str(item.self_content.id),
                    "title": item.self_content.title
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
    
    
    # 빙고판 수정하기
    def put(self, request, *args, **kwargs):
        user = request.user
        bingo = Bingo.objects.get(user=user, is_active=True)
        if not bingo:
            return Response({'error': 'No active bingo found'}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        bingo_obj = request.data.get('bingo_obj')

        if start_date:
            bingo.start_date = start_date

        if end_date:
            bingo.end_date = end_date

        if bingo_obj:

            for index, item in enumerate(bingo_obj):
                choice = item.get('choice')     # 직접 입력 항목이면 "0", 끌어온 항목이면 "1"
                item_id = item.get('id')
                item_id = int(item_id)      # item_id를 정수 처리
                title = item.get('title')

                bingo_spaces = BingoSpace.objects.filter(bingo=bingo).order_by('location')
                for bingo_space in bingo_spaces:

                    # item이 null이 아닌 경우
                    if item:
                        # 끌어오기 항목의 경우
                        if choice == "1":
                            recommend_content = ProvidedBingoItem.objects.get(id=item_id)
                            bingo_space.recommend_content = recommend_content
                            bingo_space.self_content = None
                            bingo_space.save()
                        # 직접 입력 항목의 경우
                        elif choice == "0":
                            # item_id가 있는 경우(이미 있는 직접 입력 항목의 경우)
                            if item_id != "":
                                self_content = CustomBingoItem.objects.get(id=item_id)
                                bingo_space.self_content = self_content
                                bingo_space.recommend_content = None
                                bingo_space.save()
                            # item_id가 없는 경우(새로 생성한 항목의 경우)
                            else:
                                self_content = CustomBingoItem.objects.create(user=user, title=title)
                                bingo_space.self_content = self_content
                                bingo_space.recommend_content = None
                                bingo_space.save()
                        # choice의 형식이 잘못된 경우
                        else:
                            return Response({'error': 'choice field should be 0 or 1'}, status=status.HTTP_400_BAD_REQUEST)

        bingo.change_chance -= 1        # 빙고 수정 기회 줄이기     
        bingo.save()

        return Response({
            'message': 'bingo set up success',
            'username': user.username,
            'change_chance': bingo.change_chance
        }, status=status.HTTP_200_OK)
    
# 빙고 항목 APIView    
class BingoItemAPIView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    queryset = CustomBingoItem.objects.all()
    serializer_class = BingoItemSerializer
    lookup_field_kwarg = "item_id"

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, IsAuthor]
        return super(BingoItemAPIView, self).get_permissions()

"""
    빙고 항목 APIView
    /bingo/items/12341241/ 이런식으로 요청이 올거임.
    맨 마지막 id가 뭐냐에 따라서 

"""
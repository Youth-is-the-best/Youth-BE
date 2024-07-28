from rest_framework.views import APIView
from rest_framework import generics
from users.models import CustomUser
from .models import Bingo, BingoSpace, ProvidedBingoItem, CustomBingoItem, ToDo
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .serializers import *
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

        print(f"Request data: {request.data}")

        if not isinstance(size, int) or not size in [9, 16]:
            return Response({'error': 'size field should be 9 or 16'}, status=status.HTTP_400_BAD_REQUEST)
        
        #기존에 생성되다 만 Bingo객체를 모두 비활성 처리
        inactive = Bingo.objects.filter(user=user, is_active=True)
        for bingo in inactive:
            bingo.is_active = False
            bingo.save()
            
        Bingo.objects.create(user=user, size=size, start_date=start_date, end_date=end_date)
        bingo = Bingo.objects.get(user=user, is_active=True)

        for item in bingo_obj:
            # null이 아닌 경우
            if item:
                location = item.get('location')     # 빙고 칸의 위치
                choice = item.get('choice')     # 직접 입력 항목이면 "0", 끌어온 항목이면 "1"
                item_id = item.get('id')
                if item_id:
                    item_id = int(item_id)      # item_id를 정수 처리
                title = item.get('title')

                if not choice:      # choice 입력하지 않으면 에러
                    return Response({'error': 'choice 필드를 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 직접 입력한 항목의 경우
                if choice == "0":
                    self_content = CustomBingoItem.objects.create(author=user, title=title)
                    BingoSpace.objects.create(user=user, bingo=bingo, self_content=self_content, location=location, start_date=None, end_date=None)

                # 끌어온 항목의 경우
                elif choice == "1":
                    recommend_content = ProvidedBingoItem.objects.get(id=item_id)
                    BingoSpace.objects.create(user=user, bingo=bingo, recommend_content=recommend_content, location=location)
                # 잘못된 choice 형식의 경우
                else:
                    return Response({'error': 'choice 필드는 "0" 또는 "1"입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
            # null인 경우
            if not item:
                BingoSpace.objects.create(user=user, bingo=bingo, location=location)

        return Response({
            'message': '빙고가 성공적으로 생성 되었습니다.',
            'user': user.username,
            'change_chance': bingo.change_chance
        }, status=status.HTTP_200_OK)
    

    # 빙고 판 정보 불러오기
    def get(self, request, *args, **kwargs):
        user = request.user
        bingo = Bingo.objects.get(user=user, is_active=True)

        if not bingo:
            return Response({'error': '빙고판 불러오기에 실패하였습니다. 백엔드에게 문의 주세요'}, status=status.HTTP_404_NOT_FOUND)
        
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
            return Response({'error': '빙고판 불러오기에 실패하였습니다. 백엔드에게 문의 주세요'}, status=status.HTTP_404_NOT_FOUND)
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        bingo_obj = request.data.get('bingo_obj')

        if start_date:
            bingo.start_date = start_date

        if end_date:
            bingo.end_date = end_date

        if bingo_obj:

            for item in bingo_obj:
                location = item.get('location')     # 빙고 위치
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
                            bingo_space.location = location
                            bingo_space.save()
                        # 직접 입력 항목의 경우
                        elif choice == "0":
                            # item_id가 있는 경우(이미 있는 직접 입력 항목의 경우)
                            if item_id != "":
                                self_content = CustomBingoItem.objects.get(id=item_id)
                                bingo_space.self_content = self_content
                                bingo_space.recommend_content = None
                                bingo_space.location = location
                                bingo_space.save()
                            # item_id가 없는 경우(새로 생성한 항목의 경우)
                            else:
                                self_content = CustomBingoItem.objects.create(user=user, title=title)
                                bingo_space.self_content = self_content
                                bingo_space.recommend_content = None
                                bingo_space.location = location
                                bingo_space.save()
                        # choice의 형식이 잘못된 경우
                        else:
                            return Response({'error': 'choice 필드는 "0" 또는 "1"입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        bingo.change_chance -= 1        # 빙고 수정 기회 줄이기     
        bingo.save()

        return Response({
            'message': 'bingo set up success',
            'username': user.username,
            'change_chance': bingo.change_chance
        }, status=status.HTTP_200_OK)
    

class BingoObjAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAuthor]
    
    def get(self, request, obj_id, *args, **kwargs):
        try:
            target = BingoSpace.objects.get(id=obj_id)
        except BingoSpace.DoesNotExist:
            return Response({"error": "요청한 빙고항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        try: 
            data = {}
            # 1. 빙고 칸 정보 불러오기
            target_serialized = BingoSpaceSerializer(target)
            data['bingo_space'] = target_serialized

            # 2. 빙고 항목 정보 불러오기
            if target.recommend_content:
                assert(target.self_content == False)
                item = ProvidedBingoItem.objects.get(target.recommend_content)
                item_serialized = ProvidedBingoItemSerializer(item)
                data['bingo_item'] = item_serialized

            if target.self_content:
                assert(target.recommend_content == False)
                item = CustomBingoItem.objects.get(target.self_content)
                item_serialized = CustomBingoItemSerializer(item)
                data['bingo_item'] = item_serialized

            # 3. 빙고 칸의 투두 항목 정보 불러오기
                todo = ToDo.objects.filter(bingo_space=target)
                todo_serialized = ToDoSerializer(todo, many=True)
                data['todo'] = todo_serialized

            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "서버 오류가 발생했습니다. 백엔드를 위로해주세요."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, obj_id, *args, **kwargs):
        try:
            target = BingoSpace.objects.get(id=obj_id)
        except BingoSpace.DoesNotExist:
            return Response({"error": "요청한 빙고항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        try: 
            serializer = BingoSpaceSerializer(target, data=request.data.get('bingo_space'))
            if serializer.is_valid():
                serializer.save()

            #사실상 비어있는 BingoSpace에 채워야할 경우도 있기 때문에 target으로부터 바로 종류를 가져올 수 없을 수 있다.
            choice = request.data.get('choice')
            if choice == "0": #직접입력의 경우
                serializer = CustomBingoItemSerializer(target.self_content, data=request.data.get('bingo_item'))
                if serializer.is_valid():
                    serializer.save()
            elif choice == "1": #끌어오기항목의 경우
                serializer = ProvidedBingoItemSerializer(target.recommend_content, data=request.data.get('bingo_item'))
                if serializer.is_valid():
                    serializer.save()
            else:
                raise ValueError('choice 값은 \'0\' 또는 \'1\'만 가능합니다.')
            
            serializer = ToDoSerializer(target, data=request.data.get['todo'], many=True)
            if serializer.is_valid():
                serializer.save()

        except Exception as e:
            return Response({"error": "형식이 올바르지 못한 요청입니다.", "err_msg": e}, status=status.HTTP_400_BAD_REQUEST)                                                
                
        return Response({"success": "정상적으로 수정되었습니다."}, status=status.HTTP_200_OK)
        
    def delete(self, request, obj_id, *args, **kwargs):
        try:
            target = BingoSpace.objects.get(id=obj_id)
        except BingoSpace.DoesNotExist:
            return Response({"error": "요청한 빙고항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        #만약 init 안된 빙고칸을 삭제하려 한다면
        if target.recommend_content is False and target.self_content is False:
            return Response({"error": "빙고항목이 이미 비어있습니다."}, status=status.HTTP_202_ACCEPTED)
        
        try:
            #투두 삭제
            todo = ToDo.objects.filter(bingo_space=target)
            todo.delete()

            #빙고 항목 삭제
            if target.self_content:
                item = CustomBingoItem.objects.get(target.self_content)
                item.delete()

            #빙고 칸 초기화
            pk_field_name = target._meta.pk.name
            for field in target._meta.get_fields():
                fields_to_leave = [pk_field_name, 'user', 'bingo', 'location']
                if not field.name in fields_to_leave:
                    setattr(target, field.name, None)
        except Exception as e:
            return Response({"error": "서버 오류 발생. 에러 메시지를 백엔드에게 보여주세요.", "err_msg": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        return Response({"success": "정상적으로 삭제되었습니다."}, status=status.HTTP_200_OK)     

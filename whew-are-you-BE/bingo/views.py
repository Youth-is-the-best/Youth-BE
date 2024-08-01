from rest_framework.views import APIView
from rest_framework import generics
from users.models import CustomUser
from .models import Bingo, BingoSpace, ProvidedBingoItem, CustomBingoItem, ToDo
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .serializers import *
from users.permissions import IsAuthor
from .permissions import IsValidLoc
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from review_information.serializers import InformationGETSerializer, ReviewGETSerializer


# 빙고 저장 & 불러오기
class BingoAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

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
                item_id = item.get('id')        # 추천 항목의 경우만 처음부터 item_id를 갖는다.
                if item_id:
                    item_id = int(item_id)      # item_id를 정수 처리
                title = item.get('title')
                todos = item.get('todo')

                if not choice:      # choice 입력하지 않으면 에러
                    return Response({'error': 'choice 필드를 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 직접 입력한 항목의 경우
                if choice == "0":
                    self_content = CustomBingoItem.objects.create(author=user, title=title)
                    bingo_space = BingoSpace.objects.create(user=user, bingo=bingo, self_content=self_content, location=location, start_date=None, end_date=None)

                # 끌어온 항목의 경우
                elif choice == "1":
                    recommend_content = ProvidedBingoItem.objects.get(id=item_id)
                    bingo_space = BingoSpace.objects.create(user=user, bingo=bingo, recommend_content=recommend_content, location=location)
                # 잘못된 choice 형식의 경우
                else:
                    return Response({'error': 'choice 필드는 "0" 또는 "1"입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                
                #투두 등록하기
                for todo in todos:
                    ToDo.objects.create(title=todo['title'], bingo=bingo, bingo_space=bingo_space, user=user)
                
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

        if user.is_authenticated:
            try:
                bingo = Bingo.objects.get(user=user, is_active=True)
            except Bingo.DoesNotExist:
                bingo = None
        else:
            bingo = None

        if not bingo:
            return Response({'error': '빙고판 불러오기에 실패하였습니다.'}, status=status.HTTP_404_NOT_FOUND)
        
        bingo_spaces = BingoSpace.objects.filter(bingo=bingo).order_by('location')
        bingo_obj = []
        
        for item in bingo_spaces:
            # 빙고 칸의 실행 여부 is_executed (실행 되었으면 1, 안 되었으면 0)
            if item.is_executed == True:
                is_executed = 1
            else:
                is_executed = 0

            #item의 투두 항목 모두 불러오기 (신박함)
            todos = item.todo.all() 

            if item.recommend_content:
                bingo_obj.append({
                    "location": item.location,
                    "is_executed": is_executed,
                    "choice": "1",
                    "item_id": item.id,
                    "content_id": str(item.recommend_content.id),
                    "title": item.recommend_content.title,
                    "todo": ToDoSerializer(todos, many=True).data
                })
            elif item.self_content:
                bingo_obj.append({
                    "location": item.location,
                    "is_executed": is_executed,
                    "choice": "0",
                    "item_id": item.id,
                    "content_id": str(item.self_content.id),
                    "title": item.self_content.title,
                    "todo": ToDoSerializer(todos, many=True).data
                })
            else:
                bingo_obj.append(None)
        
        user_type = user.type_result.user_type

        if user_type == 'SQUIRREL':
            user_type = '준비성 철저한 다람쥐'
        elif user_type == 'RABBIT':
            user_type = '열정 가득 부지런한 토끼'
        elif user_type == 'PANDA':
            user_type = '재충전을 원하는 판다'
        elif user_type == 'BEAVER':
            user_type = '끝없는 발전을 추구하는 비버'
        elif user_type == 'EAGLE':
            user_type = '모험을 갈망하는 독수리'
        elif user_type == 'BEAR':
            user_type = '안정을 추구하는 곰'
        elif user_type == 'DOLPHIN':
            user_type = '호기심 많은 돌고래'

        return Response({
            "username": user.username,
            "usertype": user_type,
            "start_date": bingo.start_date,
            "end_date": bingo.end_date,
            "size": bingo.size,
            "bingo_obj": bingo_obj
        }, status=status.HTTP_200_OK)
    
    

class BingoObjAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAuthor, IsValidLoc]
    
    def get(self, request, location, *args, **kwargs):
        try:
            location = int(location)
            bingo = Bingo.objects.get(user=request.user, is_active=True)
            target = BingoSpace.objects.get(bingo=bingo, location=location)
        except BingoSpace.DoesNotExist:
            return Response({"error": "요청한 빙고항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        try: 
            data = {}
            # 1. 빙고 칸 정보 불러오기
            target_serialized = BingoSpaceSerializer(target)
            data['bingo_space'] = target_serialized.data

            # 2. 빙고 항목 정보 불러오기
            if target.recommend_content:
                assert(target.self_content is None)
                try:
                    item = ProvidedBingoItem.objects.get(id=target.recommend_content.id)
                except Exception as e:
                    print("ProvidedBingoItem 가져오는 중 오류", e, type(e))
                    raise e
                item_serialized = ProvidedBingoItemSerializer(item)
                data['bingo_item'] = item_serialized.data

            if target.self_content:
                assert(target.recommend_content is None)
                try:
                    item = CustomBingoItem.objects.get(id=target.self_content.id)
                except Exception as e:
                    print("CustomBingoItem 가져오는 중 오류", e, type(e))
                    raise e
                item_serialized = CustomBingoItemSerializer(item)
                data['bingo_item'] = item_serialized.data

            # 3. 빙고 칸의 투두 항목 정보 불러오기
            todo = ToDo.objects.filter(bingo_space=target)
            todo_serialized = ToDoSerializer(todo, many=True)
            data['todo'] = todo_serialized.data

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Exception: {e}, Type: {type(e)}")
            return Response({"error": "서버 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, location, *args, **kwargs):
        try:
            location = int(location)
            bingo = Bingo.objects.get(user=request.user, is_active=True)
            target = BingoSpace.objects.get(bingo=bingo, location=location)
        except BingoSpace.DoesNotExist:
            return Response({"error": "요청한 빙고항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        bingo_pan = Bingo.objects.get(id=target.bingo.id)
        if not bingo_pan.change_chance > 0:
            return Response({'error': '빙고 수정 기회를 모두 소진하였습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            serializer = BingoSpaceSerializer(target, data=request.data.get('bingo_space'))
            if serializer.is_valid():
                #TODO: 원래는 is_executed 등 함부로 못 바꾸게 sanitize 해야.
                serializer.save()

            # choice 변수 대신 자동으로 수정 가능 여부 판단
            if target.self_content is not None and target.recommend_content is None: # 직접입력의 경우
                serializer = CustomBingoItemSerializer(target.self_content, data=request.data.get('bingo_item'))
                if serializer.is_valid(): 
                    serializer.save() # 들어온 그대로 바꿔준다.
            elif target.recommend_content is not None and target.self_content is None: # 끌어오기항목의 경우
                pass # 수정 불가하므로 아무 수정도 하지 않는다.
            else:
                return Response({'error': "BingoSpace 객체에 문제가 있습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            todos_data = request.data.get('todo', [])
            existing_todo_ids = set(ToDo.objects.filter(bingo_space=target).values_list('id', flat=True))
            request_todo_ids = set()
            for todo_data in todos_data:
                todo_id = todo_data.get('id')
                if todo_id:
                    request_todo_ids.add(todo_id)
                    try:
                        todo = ToDo.objects.get(id=todo_id)
                        todo_serializer = ToDoSerializer(todo, data=todo_data)
                    except ToDo.DoesNotExist:
                        todo_serializer = ToDoSerializer(data=todo_data)
                else:
                    todo_serializer = ToDoSerializer(data=todo_data)

                if todo_serializer.is_valid():
                    todo_serializer.save(bingo_space=target)
            to_delete_ids = existing_todo_ids - request_todo_ids
            ToDo.objects.filter(id__in=to_delete_ids).delete()

        except Exception as e:
            return Response({"error": "형식이 올바르지 못한 요청입니다.", "err_msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)                                                

        bingo_pan.change_chance -= 1
        bingo_pan.save()

        return Response({"success": "정상적으로 수정되었습니다.", "change_chance": bingo_pan.change_chance}, status=status.HTTP_200_OK)
        
    def delete(self, request, location, *args, **kwargs):
        try:
            location = int(location)
            bingo = Bingo.objects.get(user=request.user, is_active=True)
            target = BingoSpace.objects.get(bingo=bingo, location=location)
        except BingoSpace.DoesNotExist:
            return Response({"error": "요청한 빙고항목이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        #만약 init 안된 빙고칸을 삭제하려 한다면
        if target.recommend_content is None and target.self_content is None:
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


# 빙고 인증용 후기글 뷰
class BingoReviewAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = ReviewPOSTSerializer(data=request.data, context={'request':request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BingoRecsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        param_value = request.GET.get('type', None)

        if param_value not in ['squirrel', 'rabbit', 'panda', 'beaver', 'eagle', 'bear', 'dolphin']:
            return Response({"error": "type 쿼리 필드가 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            #일단 대강 일케 추천
            recs = ProvidedBingoItem.objects.filter(type__user_type = param_value.upper())
            serializer = ProvidedBingoItemSerializer(recs, many=True)
            serializer_data = serializer.data

        return Response({"success": "유형별 추천 항목", "data": serializer_data}, status=status.HTTP_200_OK)

class BingoUpcomingAPIView(generics.ListAPIView):
    queryset = ProvidedBingoItem.objects.filter(app_due__gte=timezone.now()).order_by('app_due')
    serializer_class = ProvidedBingoItemSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 12  # Limit to 10 results per page

class BingoSavedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        stored_reviews = user.storage_review.all()
        stored_reviews = ReviewGETSerializer(stored_reviews, many=True).data
        # 이런식으로 공고도 불러오기(info가 아니라 notice 가 들어와야 함, info는 빙고로 못 끌어간다.)
        stored_info = user.storage_information.all()
        stored_info = InformationGETSerializer(stored_info, many=True).data
        return Response({"success": "저장된 항목", "stored_reviews": stored_reviews, "stored_notices": stored_info}, status=status.HTTP_200_OK)

class BingoItemAPIView(generics.RetrieveAPIView):
    queryset = ProvidedBingoItem.objects.all()
    serializer_class = ProvidedBingoItemSerializer
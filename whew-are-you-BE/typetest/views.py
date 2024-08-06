from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Question, Answer, Choice, Type
from .serializers import QuestionSerializer, AnswerSerializer, ChoiceSerializer
from django.conf import settings
import copy


# 질문 받아오는 api
class QuestionListAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 선지 받아오는 api
class ChoiceListAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        choices = Choice.objects.all()
        serializer = ChoiceSerializer(choices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 사용자가 입력한 값을 전달하는 api
class SubmitAnswerAPIView(APIView):

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None      # 사용자가 로그인한 상태이면 user 설정, 아니면 None으로 설정
        return_year = request.data.get('return_year')
        return_semester = request.data.get('return_semester')
        answer2 = request.data.get('answer2')
        answer3 = request.data.get('answer3', [])
        answer4 = request.data.get('answer4')

        scores = { 'SQUIRREL': 0, 'RABBIT': 0, 'PANDA': 0, 'BEAVER': 0, 'EAGLE': 0, 'BEAR': 0, 'DOLPHIN': 0 }

        if not return_year:
            return Response({'error': 'return_year is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not return_semester:
            return Response({'error': 'return_semester is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not answer2:
            return Response({'error': 'answer2 is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not answer3:
            return Response({'error': 'answer3 is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not answer4:
            return Response({'error': 'answer4 is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if answer2 not in ['jobPreparation', 'internship', 'academicStress', 'selfDevelopment', 'diverseExperiences', 'financialBurden', 'mentalStability', 'newCareerExploration']:
            return Response({'error': 'Invalid answer_text'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 2번 문항의 가중치 15점을 특정 유형에 부여
        if answer2 == 'jobPreparation':
            scores['SQUIRREL'] += 15
        elif answer2 == 'internship':
            scores['RABBIT'] += 15
        elif answer2 == 'academicStress':
            scores['PANDA'] += 15
        elif answer2 == 'selfDevelopment':
            scores['BEAVER'] += 15
        elif answer2 == 'diverseExperiences':
            scores['EAGLE'] += 15
        elif answer2 == 'financialBurden':
            scores['BEAR'] += 15
        elif answer2 == 'mentalStability':
            scores['PANDA'] += 15
        elif answer2 == 'newCareerExploration':
            scores['DOLPHIN'] += 15

        # 3번 문항의 가중치를 사용자의 선택에 따라 부여
        rank_points = [5, 4, 3, 2, 1]
        for idx, choice in enumerate(answer3):  # enumerate 함수를 통해 인덱스와 선택지를 choice로부터 받음
            if idx < len(rank_points):
                # 값이 올바르지 않으면 에러
                if choice not in ['취업 준비', '자격증 취득', '대외활동 참여', '인턴 근무', '자기계발' '대외활동 참여', '동아리활동 참여', '취미활동',
                                    '여행', '새로운 인간관계 형성', '휴식', '독서', '혼자만의 시간', '가족과의 시간', '아르바이트', '취미활동', '진로 탐색']:
                    return Response({'error': 'Invalid choices'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 선택된 활동에 따라 특정 유형에 가중치를 부여, 겹치는걸 고려해서 if문으로만 구성
                if choice in ['취업 준비', '자격증 취득', '대외활동 참여']:
                    scores['SQUIRREL'] += rank_points[idx]
                if choice in ['인턴 근무', '자기계발' '대외활동 참여', '동아리활동 참여', '취미활동']:
                    scores['RABBIT'] += rank_points[idx]
                if choice in ['여행', '새로운 인간관계 형성']:
                    scores['EAGLE'] += rank_points[idx]
                if choice in ['여행', '휴식', '독서', '혼자만의 시간', '가족과의 시간']:
                    scores['PANDA'] += rank_points[idx]
                if choice in ['자격증 취득', '자기계발']:
                    scores['BEAVER'] += rank_points[idx]
                if choice in ['아르바이트']:
                    scores['BEAR'] += rank_points[idx]
                if choice in ['취미활동', '진로 탐색']:
                    scores['DOLPHIN'] += rank_points[idx]

        user_type = max(scores, key=scores.get)
        user_type_instance = Type.objects.get(user_type=user_type)

        if user_type == 'SQUIRREL':
            user_type_display = '준비성 철저한 다람쥐'
        elif user_type == 'RABBIT':
            user_type_display = '열정 가득 부지런한 토끼'
        elif user_type == 'PANDA':
            user_type_display = '재충전을 원하는 판다'
        elif user_type == 'BEAVER':
            user_type_display = '끝없는 발전을 추구하는 비버'
        elif user_type == 'EAGLE':
            user_type_display = '모험을 갈망하는 독수리'
        elif user_type == 'BEAR':
            user_type_display = '안정을 추구하는 곰'
        elif user_type == 'DOLPHIN':
            user_type_display = '호기심 많은 돌고래'
        

        if user:
            # CustomUser의 type_result 필드 업데이트
            user.type_result = user_type_instance
            user.save()
        
        # 이미지 URL 생성
        image_url = None
        if user_type_instance.image:
            image_url = request.build_absolute_uri(user_type_instance.image.url)
        
        if user:
            return Response({
                'message': 'All questions answered.',
                'scores': scores,
                'user_type': user_type,
                'user_type_display': user_type_display,
                'content': user_type_instance.content,
                'image': image_url,
                "username": user.username
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'All questions answered.',
            'scores': scores,
            'user_type': user_type,
            'content': user_type_instance.content,
            'image': image_url
        }, status=status.HTTP_200_OK)
    

# 유형 결과 공유
class ResultAPIView(APIView):
    def get(self, request, type, *args, **kwargs):
        try:
            result = Type.objects.get(user_type=type)
        except:
            return Response({"error": "해당 타입 결과가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이미지 URL 생성
        if result.image:
            image_url = request.build_absolute_uri(result.image.url)

        if type == 'SQUIRREL':
            type = '준비성 철저한 다람쥐'
        elif type == 'RABBIT':
            type = '열정 가득 부지런한 토끼'
        elif type == 'PANDA':
            type = '재충전을 원하는 판다'
        elif type == 'BEAVER':
            type = '끝없는 발전을 추구하는 비버'
        elif type == 'EAGLE':
            type = '모험을 갈망하는 독수리'
        elif type == 'BEAR':
            type = '안정을 추구하는 곰'
        elif type == 'DOLPHIN':
            type = '호기심 많은 돌고래'

        return Response({
            "message": "유형 결과입니다.",
            "user_type": type,
            "content": result.content,
            "image": image_url,
        })
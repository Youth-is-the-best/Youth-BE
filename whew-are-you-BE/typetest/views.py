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
    
    # 유형별 가중치를 저장하기 위함, 점수 누적을 위해 세션을 사용(비로그인 사용자를 위해)
    def initialize_scores(self, request):
        if 'scores' not in request.session:
            request.session['scores'] = { 'SQUIRREL': 0, 'RABBIT': 0, 'PANDA': 0, 'BEAVER': 0, 'EAGLE': 0, 'BEAR': 0, 'DOLPHIN': 0 }
        if 'scores2' not in request.session:
            request.session['scores2'] = { 'SQUIRREL': 0, 'RABBIT': 0, 'PANDA': 0, 'BEAVER': 0, 'EAGLE': 0, 'BEAR': 0, 'DOLPHIN': 0 }
        if 'scores3' not in request.session:
            request.session['scores3'] = { 'SQUIRREL': 0, 'RABBIT': 0, 'PANDA': 0, 'BEAVER': 0, 'EAGLE': 0, 'BEAR': 0, 'DOLPHIN': 0 }

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None      # 사용자가 로그인한 상태이면 user 설정, 아니면 None으로 설정
        question_id = request.data.get('question_id')                       # 질문 번호(1 ~ 4번 설정)
        answer_text = request.data.get('answer_text')                       # 답변 텍스트(1번, 2번, 4번)
        choices = request.data.get('choices', [])                           # 사용자가 선택한 복수선택 선지(3번)
        return_year = request.data.get('return_year')                       # 복학 년도
        return_semester = request.data.get('return_semester')               # 복학 학기

        try:
            question = Question.objects.get(id=question_id)                 # 질문을 불러옴
        except Question.DoesNotExist:                                       # 해당하는 질문 번호가 존재하지 않으면 400에러
            return Response({'error': 'Invalid question ID'}, status=status.HTTP_400_BAD_REQUEST)

        # 로그인 상태면 DB에 데이터를 생성
        if user:
            # 1번 질문이면 복학 시기를 저장
            if question_id == 1:
                Answer.objects.create(user=user, question=question, return_year=return_year, return_semester=return_semester)
            else:
                Answer.objects.create(user=user, question=question, answer_text=answer_text)

        # 일단 각 유형에 대한 총점을 0점으로 초기화
        self.initialize_scores(request)
        scores = request.session['scores']
        scores2 = request.session['scores2']
        scores3 = request.session['scores3']

        if question_id == 1:
                if not return_year:
                    return Response({'error': 'return_year is required'}, status=status.HTTP_400_BAD_REQUEST)
                if not return_semester:
                    return Response({'error': 'return_semester is required'}, status=status.HTTP_400_BAD_REQUEST)

        elif question_id == 2:
            scores2['SQUIRREL'] = 0
            scores2['RABBIT'] = 0
            scores2['PANDA'] = 0
            scores2['BEAVER'] = 0
            scores2['EAGLE'] = 0
            scores2['BEAR'] = 0
            scores2['DOLPHIN'] = 0

            # 에러 발생
            if not answer_text:
                return Response({'error': 'answer_text is required'}, status=status.HTTP_400_BAD_REQUEST)
            if answer_text not in ['jobPreparation', 'internship', 'academicStress', 'selfDevelopment', 'diverseExperiences', 'financialBurden', 'mentalStability', 'newCareerExploration']:
                return Response({'error': 'Invalid answer_text'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 2번 문항의 가중치 15점을 특정 유형에 부여
            if answer_text == 'jobPreparation':
                scores2['SQUIRREL'] += 15
            elif answer_text == 'internship':
                scores2['RABBIT'] += 15
            elif answer_text == 'academicStress':
                scores2['PANDA'] += 15
            elif answer_text == 'selfDevelopment':
                scores2['BEAVER'] += 15
            elif answer_text == 'diverseExperiences':
                scores2['EAGLE'] += 15
            elif answer_text == 'financialBurden':
                scores2['BEAR'] += 15
            elif answer_text == 'mentalStability':
                scores2['PANDA'] += 15
            elif answer_text == 'newCareerExploration':
                scores2['DOLPHIN'] += 15

        elif question_id == 3:
            scores3['SQUIRREL'] = 0
            scores3['RABBIT'] = 0
            scores3['PANDA'] = 0
            scores3['BEAVER'] = 0
            scores3['EAGLE'] = 0
            scores3['BEAR'] = 0
            scores3['DOLPHIN'] = 0

            # 에러
            if not choices:
                return Response({'error': 'choices is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3번 문항의 가중치를 사용자의 선택에 따라 부여
            rank_points = [5, 4, 3, 2, 1]
            for idx, choice in enumerate(choices):  # enumerate 함수를 통해 인덱스와 선택지를 choice로부터 받음
                if idx < len(rank_points):
                    # 값이 올바르지 않으면 에러
                    if choice not in ['취업 준비', '자격증 취득', '대외활동 참여', '인턴 근무', '자기계발' '대외활동 참여', '동아리활동 참여', '취미활동',
                                      '여행', '새로운 인간관계 형성', '휴식', '독서', '혼자만의 시간', '가족과의 시간', '아르바이트', '취미활동', '진로 탐색']:
                        return Response({'error': 'Invalid choices'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # 선택된 활동에 따라 특정 유형에 가중치를 부여, 겹치는걸 고려해서 if문으로만 구성
                    if choice in ['취업 준비', '자격증 취득', '대외활동 참여']:
                        scores3['SQUIRREL'] += rank_points[idx]
                    if choice in ['인턴 근무', '자기계발' '대외활동 참여', '동아리활동 참여', '취미활동']:
                        scores3['RABBIT'] += rank_points[idx]
                    if choice in ['여행', '새로운 인간관계 형성']:
                        scores3['EAGLE'] += rank_points[idx]
                    if choice in ['여행', '휴식', '독서', '혼자만의 시간', '가족과의 시간']:
                        scores3['PANDA'] += rank_points[idx]
                    if choice in ['자격증 취득', '자기계발']:
                        scores3['BEAVER'] += rank_points[idx]
                    if choice in ['아르바이트']:
                        scores3['BEAR'] += rank_points[idx]
                    if choice in ['취미활동', '진로 탐색']:
                        scores3['DOLPHIN'] += rank_points[idx]

        elif question_id == 4:
            # 에러 발생
            if not answer_text:
                return Response({'error': 'answer_text is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 업데이트된 점수를 저장
        request.session['scores2'] = scores2
        request.session['scores3'] = scores3

        # 다음 질문을 검색
        next_question = Question.objects.filter(id__gt=question_id).first()

        # 다음 질문이 있으면 다음 질문을 제공
        if next_question:
            next_question_data = QuestionSerializer(next_question).data
            return Response({
                'message': 'Answer submitted successfully.',
                'scores2': scores2,
                'scores3': scores3,
                'next_question': next_question_data
            }, status=status.HTTP_200_OK)
        
        # 다음 질문이 없으면 최종 결과를 계산
        else:

            # 최종 점수
            scores['SQUIRREL'] = scores2['SQUIRREL'] + scores3['SQUIRREL']
            scores['RABBIT'] = scores2['RABBIT'] + scores3['RABBIT']
            scores['PANDA'] = scores2['PANDA'] + scores3['PANDA']
            scores['BEAVER'] = scores2['BEAVER'] + scores3['BEAVER']
            scores['EAGLE'] = scores2['EAGLE'] + scores3['EAGLE']
            scores['BEAR'] = scores2['BEAR'] + scores3['BEAR']
            scores['DOLPHIN'] = scores2['DOLPHIN'] + scores3['DOLPHIN']

            scores_result = copy.deepcopy(scores)
            user_type = max(scores_result, key=scores.get)
            user_type_instance = Type.objects.get(user_type=user_type)

            if user:
                # CustomUser의 type_result 필드 업데이트
                user.type_result = user_type_instance
                user.save()

            self.initialize_scores(request)
                
            return Response({
                'message': 'All questions answered.',
                'scores': scores_result,
                'user_type': user_type
            }, status=status.HTTP_200_OK)
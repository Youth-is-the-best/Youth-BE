from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Question, Answer, Choice, Type
from .serializers import QuestionSerializer, AnswerSerializer, ChoiceSerializer
from django.conf import settings


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
            request.session['scores'] = {
                'CHALLENGER': 0,
                'ACTIVIST': 0,
                'RESTER': 0,
                'LEARNER': 0,
                'TRAVELER': 0,
                'STRATEGIST': 0,
                'EXPLORER': 0
            }

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

        if question_id == 2:
            # 2번 문항의 가중치 15점을 특정 유형에 부여
            if answer_text == 'jobPreparation':
                scores['CHALLENGER'] += 15
            elif answer_text == 'internship':
                scores['ACTIVIST'] += 15
            elif answer_text == 'academicStress':
                scores['RESTER'] += 15
            elif answer_text == 'selfDevelopment':
                scores['LEARNER'] += 15
            elif answer_text == 'diverseExperiences':
                scores['TRAVELER'] += 15
            elif answer_text == 'financialBurden':
                scores['STRATEGIST'] += 15
            elif answer_text == 'mentalStability':
                scores['RESTER'] += 15
            elif answer_text == 'newCareerExploration':
                scores['EXPLORER'] += 15

        elif question_id == 3:
            # 3번 문항의 가중치를 사용자의 선택에 따라 부여
            rank_points = [5, 4, 3, 2, 1]
            for idx, choice in enumerate(choices):  # enumerate 함수를 통해 인덱스와 선택지를 choice로부터 받음
                if idx < len(rank_points):
                    # 선택된 활동에 따라 특정 유형에 가중치를 부여, 겹치는걸 고려해서 if문으로만 구성
                    if choice in ['취업 준비', '자격증 취득', '대외활동 참여']:
                        scores['CHALLENGER'] += rank_points[idx]
                    if choice in ['인턴 근무', '자기계발' '대외활동 참여', '동아리활동 참여', '취미활동']:
                        scores['ACTIVIST'] += rank_points[idx]
                    if choice in ['여행', '새로운 인간관계 형성']:
                        scores['TRAVELER'] += rank_points[idx]
                    if choice in ['여행', '휴식', '독서', '혼자만의 시간', '가족과의 시간']:
                        scores['RESTER'] += rank_points[idx]
                    if choice in []:
                        scores['LEARNER'] += rank_points[idx]
                    if choice in ['아르바이트']:
                        scores['STRATEGIST'] += rank_points[idx]
                    if choice in ['취미활동', '진로 탐색']:
                        scores['EXPLORER'] += rank_points[idx]


        # 업데이트된 점수를 저장
        request.session['scores'] = scores

        # 다음 질문을 검색
        next_question = Question.objects.filter(id__gt=question_id).first()

        # 다음 질문이 있으면 다음 질문을 제공
        if next_question:
            next_question_data = QuestionSerializer(next_question).data
            return Response({
                'message': 'Answer submitted successfully.',
                'scores': scores,
                'next_question': next_question_data
            }, status=status.HTTP_200_OK)
        # 다음 질문이 없으면 최종 결과를 계산
        else:
            user_type = max(scores, key=scores.get)
            if user:
                Type.objects.create(user=user, user_type=user_type)
            return Response({
                'message': 'All questions answered.',
                'scores': scores,
                'user_type': user_type
            }, status=status.HTTP_200_OK)
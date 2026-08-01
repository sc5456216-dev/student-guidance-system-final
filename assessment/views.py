from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsStudent, IsAdvisor, IsStaffOrAdmin, IsStudentOrAdvisor, IsAdvisorOrStaffOrAdmin
from .models import Question, AssessmentResult
from .serializers import QuestionSerializer, AssessmentResultSerializer
from course.models import Course


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.filter(is_deleted=False)
    serializer_class = QuestionSerializer

    def get_permissions(self):
       
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        return [IsAuthenticated(), IsAdvisorOrStaffOrAdmin()]


class AssessmentResultViewSet(viewsets.ModelViewSet):
    queryset = AssessmentResult.objects.filter(is_deleted=False)
    serializer_class = AssessmentResultSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsStudent()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            
            return [IsAuthenticated(), IsAdvisorOrStaffOrAdmin()]
        
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == 'student':
            qs = qs.filter(student=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated(), IsStudent()])
    def submit(self, request):
        answers = request.data.get('answers', [])

        if not answers:
            return Response(
                {"error": "No answers provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course_scores = {}
        for ans in answers:
            try:
                q = Question.objects.get(id=ans['question_id'])
            except Question.DoesNotExist:
                continue

            if q.correct_option == ans['selected']:
                course_id = q.related_course_id
                if course_id:
                    course_scores[course_id] = course_scores.get(course_id, 0) + 1

        if not course_scores:
            return Response({
                "message": "No correct answers recorded",
                "recommendations": []
            })

        top_course_ids = sorted(course_scores, key=course_scores.get, reverse=True)[:2]
        recommended_courses = Course.objects.filter(id__in=top_course_ids, is_deleted=False)

        result = AssessmentResult.objects.create(
            student=request.user,
            score=sum(course_scores.values())
        )
        result.course_recommendations.set(recommended_courses)

        return Response(AssessmentResultSerializer(result).data)
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.applications.models import Application
from apps.common.permissions import IsOwnerOrRecruiter
from apps.evaluations.services import evaluate_interview

from .models import Interview, Question
from .serializers import InterviewSerializer, QuestionAnswerSerializer
from .services import generate_interview


class InterviewViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrRecruiter]
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application"]

    def get_queryset(self):
        user = self.request.user
        qs = Interview.objects.select_related("application").prefetch_related("questions")
        if user.is_recruiter:
            return qs.filter(application__job__recruiter=user)
        return qs.filter(application__candidate=user)

    def create(self, request, *args, **kwargs):
        """Recruiter triggers AI interview generation for an application."""
        application_id = request.data.get("application")
        application = Application.objects.get(id=application_id, job__recruiter=request.user)
        interview = generate_interview(application)
        return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        interview = self.get_object()
        interview.status = Interview.Status.IN_PROGRESS
        interview.started_at = timezone.now()
        interview.save(update_fields=["status", "started_at"])
        return Response(InterviewSerializer(interview).data)

    @action(detail=True, methods=["post"], url_path="questions/(?P<question_id>[^/.]+)/answer")
    def answer(self, request, pk=None, question_id=None):
        interview = self.get_object()
        question = interview.questions.get(id=question_id)
        serializer = QuestionAnswerSerializer(question, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(answered_at=timezone.now())
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark interview complete and trigger automated evaluation."""
        interview = self.get_object()
        interview.status = Interview.Status.COMPLETED
        interview.completed_at = timezone.now()
        interview.save(update_fields=["status", "completed_at"])

        evaluation = evaluate_interview(interview)
        interview.status = Interview.Status.EVALUATED
        interview.save(update_fields=["status"])

        from apps.evaluations.serializers import EvaluationSerializer

        return Response(
            {
                "interview": InterviewSerializer(interview).data,
                "evaluation": EvaluationSerializer(evaluation).data,
            }
        )

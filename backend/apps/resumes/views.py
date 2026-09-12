from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import IsOwnerOrRecruiter

from .models import Resume
from .serializers import ResumeSerializer
from .tasks import process_resume_task


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrRecruiter]

    def get_queryset(self):
        user = self.request.user
        if user.is_recruiter:
            return Resume.objects.select_related("candidate")
        return Resume.objects.filter(candidate=user)

    def perform_create(self, serializer):
        resume = serializer.save(candidate=self.request.user)
        # Kick off async parsing (falls back to sync call if no Celery worker
        # is running, e.g. in local dev without redis).
        try:
            process_resume_task.delay(resume.id)
        except Exception:
            from .services import process_resume

            process_resume(resume)

    @action(detail=True, methods=["post"])
    def reparse(self, request, pk=None):
        resume = self.get_object()
        process_resume_task.delay(resume.id)
        return Response({"status": "reparsing queued"})

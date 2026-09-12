from pgvector.django import CosineDistance
from rest_framework import permissions, viewsets

from apps.common.permissions import IsOwnerOrRecruiter

from .models import Application
from .serializers import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrRecruiter]
    filterset_fields = ["job", "stage"]

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related("job", "candidate", "resume")
        if user.is_recruiter:
            return qs.filter(job__recruiter=user)
        return qs.filter(candidate=user)

    def perform_create(self, serializer):
        application = serializer.save(candidate=self.request.user)
        self._set_match_score(application)

    @staticmethod
    def _set_match_score(application):
        """Cache the semantic match score between the candidate's resume and the job."""
        resume = application.resume
        job = application.job
        if resume and resume.embedding is not None and job.embedding is not None:
            distance = CosineDistance("embedding", job.embedding)
            annotated = type(resume).objects.filter(id=resume.id).annotate(distance=distance).first()
            if annotated:
                similarity = max(0.0, 1.0 - annotated.distance)
                application.match_score = round(similarity * 100, 1)
                application.save(update_fields=["match_score"])

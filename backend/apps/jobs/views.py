from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.common.permissions import IsRecruiterOrAdmin
from apps.matching.services import embed_and_store_job

from .models import JobPosting
from .serializers import JobPostingSerializer


class JobPostingViewSet(viewsets.ModelViewSet):
    serializer_class = JobPostingSerializer
    permission_classes = [IsRecruiterOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "employment_type", "is_remote"]
    search_fields = ["title", "description", "requirements", "location"]
    ordering_fields = ["created_at", "salary_min", "salary_max"]

    def get_queryset(self):
        user = self.request.user
        qs = JobPosting.objects.select_related("recruiter")
        if user.is_recruiter:
            return qs
        # Candidates only see open postings.
        return qs.filter(status=JobPosting.Status.OPEN)

    def perform_create(self, serializer):
        job = serializer.save(recruiter=self.request.user)
        embed_and_store_job(job)

    def perform_update(self, serializer):
        job = serializer.save()
        embed_and_store_job(job)

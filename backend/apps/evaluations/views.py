from rest_framework import mixins, permissions, viewsets

from apps.common.permissions import IsRecruiterOrAdmin

from .models import Evaluation
from .serializers import EvaluationSerializer


class EvaluationViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Read-only for recruiters, except human override fields (PATCH)."""

    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Evaluation.objects.select_related("interview__application__job")
        if user.is_recruiter:
            return qs.filter(interview__application__job__recruiter=user)
        return qs.filter(interview__application__candidate=user)

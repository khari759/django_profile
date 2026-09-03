"""Read-only API for portfolio content, plus a write endpoint for the contact form."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Certification,
    Education,
    Experience,
    Profile,
    Project,
    SkillCategory,
)
from .serializers import (
    CertificationSerializer,
    ContactMessageSerializer,
    EducationSerializer,
    ExperienceSerializer,
    ProfileSerializer,
    ProjectSerializer,
    SkillCategorySerializer,
)

logger = logging.getLogger(__name__)


def published_projects():
    return (
        Project.objects.filter(is_published=True)
        .prefetch_related("technologies")
        .order_by("display_order", "-created_at")
    )


class ProfileView(APIView):
    """The single Profile row, or 404 with a helpful hint if none exists yet."""

    def get(self, request):
        profile = Profile.objects.first()
        if profile is None:
            return Response(
                {"detail": "No profile configured. Run `manage.py seed_portfolio`."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProfileSerializer(profile, context={"request": request}).data)


class SkillCategoryListView(generics.ListAPIView):
    serializer_class = SkillCategorySerializer
    pagination_class = None
    queryset = SkillCategory.objects.prefetch_related("skills").all()


class ExperienceListView(generics.ListAPIView):
    serializer_class = ExperienceSerializer
    pagination_class = None
    queryset = Experience.objects.prefetch_related("highlights").all()


class ProjectListView(generics.ListAPIView):
    """Supports `?tech=<slug>` and `?featured=true` filters."""

    serializer_class = ProjectSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = published_projects()
        tech = self.request.query_params.get("tech")
        if tech:
            queryset = queryset.filter(technologies__slug=tech)
        if self.request.query_params.get("featured", "").lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(is_featured=True)
        return queryset.distinct()


class ProjectDetailView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return published_projects()


class EducationListView(generics.ListAPIView):
    serializer_class = EducationSerializer
    pagination_class = None
    queryset = Education.objects.all()


class CertificationListView(generics.ListAPIView):
    serializer_class = CertificationSerializer
    pagination_class = None
    queryset = Certification.objects.all()


class ContactMessageCreateView(generics.CreateAPIView):
    """Accepts contact form submissions. Rate limited to 5 per hour per IP."""

    serializer_class = ContactMessageSerializer
    throttle_scope = "contact"

    def perform_create(self, serializer):
        message = serializer.save()
        self._notify(message)

    def _notify(self, message):
        recipient = settings.CONTACT_NOTIFY_EMAIL
        if not recipient:
            return
        subject = message.subject or f"New portfolio message from {message.name}"
        try:
            send_mail(
                subject=f"[Portfolio] {subject}",
                message=f"From: {message.name} <{message.email}>\n\n{message.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception:
            # The message is already stored; a mail outage must not fail the request.
            logger.exception("Failed to send contact notification for message %s", message.pk)


class OverviewView(APIView):
    """Everything the landing page needs in one request."""

    def get(self, request):
        context = {"request": request}
        profile = Profile.objects.first()
        return Response(
            {
                "profile": ProfileSerializer(profile, context=context).data if profile else None,
                "skill_categories": SkillCategorySerializer(
                    SkillCategory.objects.prefetch_related("skills"), many=True, context=context
                ).data,
                "experience": ExperienceSerializer(
                    Experience.objects.prefetch_related("highlights"), many=True, context=context
                ).data,
                "projects": ProjectSerializer(
                    published_projects(), many=True, context=context
                ).data,
                "education": EducationSerializer(
                    Education.objects.all(), many=True, context=context
                ).data,
                "certifications": CertificationSerializer(
                    Certification.objects.all(), many=True, context=context
                ).data,
            }
        )


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})

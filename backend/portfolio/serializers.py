"""DRF serializers exposing portfolio content as JSON for the React frontend."""

from rest_framework import serializers

from .models import (
    Certification,
    ContactMessage,
    Education,
    Experience,
    ExperienceHighlight,
    Profile,
    Project,
    Skill,
    SkillCategory,
    Technology,
)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "headline",
            "summary",
            "location",
            "email",
            "phone",
            "years_of_experience",
            "avatar",
            "resume",
            "github_url",
            "linkedin_url",
            "website_url",
            "is_available_for_work",
        ]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "proficiency"]


class SkillCategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = SkillCategory
        fields = ["id", "name", "skills"]


class ExperienceHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceHighlight
        fields = ["id", "text"]


class ExperienceSerializer(serializers.ModelSerializer):
    highlights = ExperienceHighlightSerializer(many=True, read_only=True)
    tech_list = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Experience
        fields = [
            "id",
            "company",
            "company_url",
            "role",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "tech_list",
            "highlights",
        ]


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ["id", "name", "slug"]


class ProjectSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "description",
            "role",
            "technologies",
            "thumbnail",
            "repo_url",
            "live_url",
            "is_featured",
            "started_on",
        ]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "id",
            "degree",
            "institution",
            "location",
            "start_year",
            "end_year",
            "notes",
        ]


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ["id", "name", "issuer", "issued_on", "credential_url"]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "subject", "message", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "name": {"trim_whitespace": True},
            "message": {"trim_whitespace": True},
        }

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please write at least 10 characters so I know how to help."
            )
        return value

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Please enter your name.")
        return value

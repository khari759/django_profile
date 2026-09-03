"""Model-level validation and behaviour tests."""

from datetime import date

import pytest
from django.core.exceptions import ValidationError

from portfolio.models import Experience, Profile, Project, Technology


@pytest.mark.django_db
class TestProfile:
    def test_is_a_singleton(self, profile):
        with pytest.raises(ValidationError, match="Only one Profile"):
            Profile.objects.create(
                full_name="Someone Else",
                headline="Engineer",
                summary="Another summary",
                email="other@example.com",
            )

    def test_existing_profile_can_still_be_saved(self, profile):
        profile.headline = "Senior Full Stack Engineer"
        profile.save()
        profile.refresh_from_db()
        assert profile.headline == "Senior Full Stack Engineer"


@pytest.mark.django_db
class TestExperience:
    def test_end_date_before_start_date_is_rejected(self):
        experience = Experience(
            company="Acme",
            role="Developer",
            start_date=date(2023, 3, 1),
            end_date=date(2022, 1, 1),
        )
        with pytest.raises(ValidationError) as exc:
            experience.full_clean()
        assert "end_date" in exc.value.message_dict

    def test_current_role_cannot_have_end_date(self):
        experience = Experience(
            company="Acme",
            role="Developer",
            start_date=date(2023, 3, 1),
            end_date=date(2024, 1, 1),
            is_current=True,
        )
        with pytest.raises(ValidationError) as exc:
            experience.full_clean()
        assert "end_date" in exc.value.message_dict

    def test_tech_list_splits_and_strips(self):
        experience = Experience(tech_summary="Python,  Django , React.js")
        assert experience.tech_list == ["Python", "Django", "React.js"]

    def test_tech_list_is_empty_when_unset(self):
        assert Experience(tech_summary="").tech_list == []


@pytest.mark.django_db
class TestSlugGeneration:
    def test_project_slug_derives_from_title(self):
        project = Project.objects.create(
            title="AbsoluteCORE — Payroll App",
            summary="Payroll",
            description="Long description",
        )
        assert project.slug == "absolutecore-payroll-app"

    def test_explicit_project_slug_is_respected(self):
        project = Project.objects.create(
            title="Portfolio", slug="my-site", summary="s", description="d"
        )
        assert project.slug == "my-site"

    def test_technology_slug_derives_from_name(self):
        assert Technology.objects.create(name="Django REST Framework").slug == (
            "django-rest-framework"
        )

    def test_colliding_technology_slugs_are_made_unique(self):
        # slugify() strips punctuation, so both names reduce to "c".
        first = Technology.objects.create(name="C")
        second = Technology.objects.create(name="C++")
        assert first.slug == "c"
        assert second.slug == "c-2"

    def test_colliding_project_slugs_are_made_unique(self):
        first = Project.objects.create(title="Portfolio!", summary="s", description="d")
        second = Project.objects.create(title="Portfolio?", summary="s", description="d")
        assert first.slug == "portfolio"
        assert second.slug == "portfolio-2"

    def test_slug_stays_within_the_column_limit(self):
        long_title = "Very Long Project Title " * 20
        first = Project.objects.create(title=long_title, summary="s", description="d")
        second = Project.objects.create(title=long_title, slug="", summary="s", description="d")
        assert len(first.slug) <= 180
        assert len(second.slug) <= 180
        assert first.slug != second.slug

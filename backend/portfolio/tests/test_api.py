"""API contract tests for every public endpoint."""

import pytest
from django.core import mail
from django.urls import reverse

from portfolio.models import ContactMessage


@pytest.mark.django_db
class TestHealthAndRoot:
    def test_health_returns_ok(self, api_client):
        response = api_client.get(reverse("portfolio:health"))
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root_lists_endpoints(self, api_client):
        response = api_client.get(reverse("api-root"))
        assert response.status_code == 200
        assert "/api/overview/" in response.json()["endpoints"]


@pytest.mark.django_db
class TestProfileEndpoint:
    def test_returns_profile_fields(self, api_client, profile):
        response = api_client.get(reverse("portfolio:profile"))
        assert response.status_code == 200
        body = response.json()
        assert body["full_name"] == "Hari Krishna Komire"
        assert body["headline"] == "Full Stack Software Engineer"
        assert body["is_available_for_work"] is True

    def test_missing_profile_returns_helpful_404(self, api_client):
        response = api_client.get(reverse("portfolio:profile"))
        assert response.status_code == 404
        assert "seed_portfolio" in response.json()["detail"]


@pytest.mark.django_db
class TestSkillsEndpoint:
    def test_skills_are_nested_under_categories(self, api_client, skills):
        response = api_client.get(reverse("portfolio:skills"))
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 1
        assert categories[0]["name"] == "Backend"
        assert [skill["name"] for skill in categories[0]["skills"]] == [
            "Django",
            "Django REST Framework",
        ]


@pytest.mark.django_db
class TestExperienceEndpoint:
    def test_includes_highlights_and_parsed_tech(self, api_client, experience):
        response = api_client.get(reverse("portfolio:experience"))
        assert response.status_code == 200
        role = response.json()[0]
        assert role["is_current"] is True
        assert role["end_date"] is None
        assert role["tech_list"] == ["Python", "Django", "React.js"]
        assert len(role["highlights"]) == 1


@pytest.mark.django_db
class TestProjectsEndpoint:
    def test_lists_only_published_projects(self, api_client, projects):
        response = api_client.get(reverse("portfolio:project-list"))
        assert response.status_code == 200
        titles = [project["title"] for project in response.json()]
        assert titles == ["AbsoluteCORE Payroll", "Portfolio Site"]
        assert "Work In Progress" not in titles

    def test_featured_filter(self, api_client, projects):
        response = api_client.get(reverse("portfolio:project-list"), {"featured": "true"})
        assert [p["title"] for p in response.json()] == ["AbsoluteCORE Payroll"]

    def test_tech_filter(self, api_client, projects, technologies):
        response = api_client.get(
            reverse("portfolio:project-list"), {"tech": technologies["react"].slug}
        )
        assert [p["title"] for p in response.json()] == ["Portfolio Site"]

    def test_unknown_tech_filter_returns_empty_list(self, api_client, projects):
        response = api_client.get(reverse("portfolio:project-list"), {"tech": "cobol"})
        assert response.status_code == 200
        assert response.json() == []

    def test_tech_filter_does_not_duplicate_rows(self, api_client, projects):
        response = api_client.get(reverse("portfolio:project-list"), {"tech": "django"})
        titles = [p["title"] for p in response.json()]
        assert titles == sorted(set(titles), key=titles.index)
        assert len(titles) == 2

    def test_detail_by_slug(self, api_client, projects):
        url = reverse("portfolio:project-detail", args=[projects["featured"].slug])
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.json()["description"] == "Payroll workflows, contracts and payslips."

    def test_unpublished_detail_is_hidden(self, api_client, projects):
        url = reverse("portfolio:project-detail", args=[projects["unpublished"].slug])
        assert api_client.get(url).status_code == 404


@pytest.mark.django_db
class TestOverviewEndpoint:
    def test_returns_every_section(
        self, api_client, profile, skills, experience, projects, education, certification
    ):
        response = api_client.get(reverse("portfolio:overview"))
        assert response.status_code == 200
        body = response.json()
        assert set(body) == {
            "profile",
            "skill_categories",
            "experience",
            "projects",
            "education",
            "certifications",
        }
        assert body["profile"]["full_name"] == "Hari Krishna Komire"
        assert len(body["skill_categories"]) == 1
        assert len(body["experience"]) == 1
        assert len(body["projects"]) == 2
        assert len(body["education"]) == 1
        assert len(body["certifications"]) == 1

    def test_survives_an_empty_database(self, api_client):
        response = api_client.get(reverse("portfolio:overview"))
        assert response.status_code == 200
        body = response.json()
        assert body["profile"] is None
        assert body["projects"] == []


@pytest.mark.django_db
class TestContactEndpoint:
    payload = {
        "name": "Recruiter",
        "email": "recruiter@example.com",
        "subject": "Role at Deloitte",
        "message": "We would like to discuss an opportunity with you.",
    }

    def test_valid_submission_is_stored(self, api_client):
        response = api_client.post(reverse("portfolio:contact"), self.payload, format="json")
        assert response.status_code == 201
        message = ContactMessage.objects.get()
        assert message.email == "recruiter@example.com"
        assert message.is_read is False

    def test_notification_email_is_sent_when_configured(self, api_client, settings):
        settings.CONTACT_NOTIFY_EMAIL = "owner@example.com"
        api_client.post(reverse("portfolio:contact"), self.payload, format="json")
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["owner@example.com"]
        assert "Role at Deloitte" in mail.outbox[0].subject

    def test_no_email_when_notification_address_is_unset(self, api_client, settings):
        settings.CONTACT_NOTIFY_EMAIL = ""
        api_client.post(reverse("portfolio:contact"), self.payload, format="json")
        assert mail.outbox == []

    def test_message_is_kept_even_if_mail_delivery_fails(self, api_client, settings, monkeypatch):
        settings.CONTACT_NOTIFY_EMAIL = "owner@example.com"

        def explode(*args, **kwargs):
            raise OSError("SMTP unavailable")

        monkeypatch.setattr("portfolio.views.send_mail", explode)
        response = api_client.post(reverse("portfolio:contact"), self.payload, format="json")
        assert response.status_code == 201
        assert ContactMessage.objects.count() == 1

    @pytest.mark.parametrize(
        "field,value",
        [
            ("email", "not-an-email"),
            ("message", "too short"),
            ("name", "X"),
        ],
    )
    def test_invalid_input_is_rejected(self, api_client, field, value):
        response = api_client.post(
            reverse("portfolio:contact"), {**self.payload, field: value}, format="json"
        )
        assert response.status_code == 400
        assert field in response.json()
        assert ContactMessage.objects.count() == 0

    def test_read_methods_are_not_allowed(self, api_client):
        assert api_client.get(reverse("portfolio:contact")).status_code == 405

    def test_submissions_are_rate_limited(self, api_client):
        url = reverse("portfolio:contact")
        for _ in range(5):
            assert api_client.post(url, self.payload, format="json").status_code == 201
        response = api_client.post(url, self.payload, format="json")
        assert response.status_code == 429
        assert ContactMessage.objects.count() == 5

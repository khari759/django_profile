from datetime import date

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from portfolio.models import (
    Certification,
    Education,
    Experience,
    ExperienceHighlight,
    Profile,
    Project,
    Skill,
    SkillCategory,
    Technology,
)


@pytest.fixture(autouse=True)
def clear_throttle_history():
    """DRF stores throttle counters in the cache, which outlives a test.

    Without this, tests that POST to the rate-limited contact endpoint start
    failing with 429 once the suite has made five requests in total.
    """
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def profile(db):
    return Profile.objects.create(
        full_name="Hari Krishna Komire",
        headline="Full Stack Software Engineer",
        summary="Full stack engineer working with Python, Django and React.",
        location="Bengaluru, India",
        email="hari646592@gmail.com",
        years_of_experience=4,
        github_url="https://github.com/example",
        linkedin_url="https://linkedin.com/in/example",
    )


@pytest.fixture
def skills(db):
    category = SkillCategory.objects.create(name="Backend", display_order=0)
    Skill.objects.create(category=category, name="Django", display_order=0)
    Skill.objects.create(category=category, name="Django REST Framework", display_order=1)
    return category


@pytest.fixture
def experience(db):
    role = Experience.objects.create(
        company="Infanion Software Solutions Private Ltd.",
        role="Associate Software Developer",
        location="Bengaluru, India",
        start_date=date(2023, 3, 1),
        is_current=True,
        tech_summary="Python, Django, React.js",
    )
    ExperienceHighlight.objects.create(
        experience=role, text="Built RESTful APIs with Django REST Framework.", display_order=0
    )
    return role


@pytest.fixture
def technologies(db):
    return {
        "django": Technology.objects.create(name="Django"),
        "react": Technology.objects.create(name="React.js"),
    }


@pytest.fixture
def projects(db, technologies):
    featured = Project.objects.create(
        title="AbsoluteCORE Payroll",
        summary="Enterprise payroll platform.",
        description="Payroll workflows, contracts and payslips.",
        is_featured=True,
        display_order=0,
    )
    featured.technologies.set([technologies["django"]])

    secondary = Project.objects.create(
        title="Portfolio Site",
        summary="This website.",
        description="Django API plus React frontend.",
        is_featured=False,
        display_order=1,
    )
    secondary.technologies.set([technologies["django"], technologies["react"]])

    unpublished = Project.objects.create(
        title="Work In Progress",
        summary="Not ready yet.",
        description="Hidden from the public API.",
        is_published=False,
        display_order=2,
    )
    return {"featured": featured, "secondary": secondary, "unpublished": unpublished}


@pytest.fixture
def education(db):
    return Education.objects.create(
        degree="B.Tech Civil Engineering",
        institution="Annamacharya Institute of Technology and Sciences",
        start_year=2015,
        end_year=2019,
    )


@pytest.fixture
def certification(db):
    return Certification.objects.create(
        name="Associate Developer Certification", issuer="Boomi Education Services"
    )

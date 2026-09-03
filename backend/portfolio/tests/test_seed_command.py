"""The seed command is how content gets bootstrapped, so it is covered too."""

import pytest
from django.core.management import call_command

from portfolio.models import (
    Certification,
    Education,
    Experience,
    ExperienceHighlight,
    Profile,
    Project,
    Skill,
)


@pytest.mark.django_db
class TestSeedPortfolio:
    def test_populates_every_section(self):
        call_command("seed_portfolio", verbosity=0)
        assert Profile.objects.count() == 1
        assert Skill.objects.exists()
        assert Experience.objects.count() == 3
        assert Project.objects.count() == 3
        assert Education.objects.count() == 1
        assert Certification.objects.count() == 2

    def test_is_idempotent(self):
        call_command("seed_portfolio", verbosity=0)
        counts = (
            Profile.objects.count(),
            Skill.objects.count(),
            Experience.objects.count(),
            ExperienceHighlight.objects.count(),
            Project.objects.count(),
        )
        call_command("seed_portfolio", verbosity=0)
        assert counts == (
            Profile.objects.count(),
            Skill.objects.count(),
            Experience.objects.count(),
            ExperienceHighlight.objects.count(),
            Project.objects.count(),
        )

    def test_reset_flag_reseeds_cleanly(self):
        call_command("seed_portfolio", verbosity=0)
        Project.objects.create(title="Stale entry", summary="s", description="d")
        call_command("seed_portfolio", "--reset", verbosity=0)
        assert Project.objects.count() == 3
        assert not Project.objects.filter(title="Stale entry").exists()

    def test_projects_get_technologies_attached(self):
        call_command("seed_portfolio", verbosity=0)
        project = Project.objects.get(title__startswith="AbsoluteCORE")
        assert {t.name for t in project.technologies.all()} == {
            "Python",
            "Django",
            "TypeScript",
            "Redux",
            "PostgreSQL",
        }

"""The superuser bootstrap runs on every deploy, so it is covered thoroughly."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

CREDENTIALS = {
    "DJANGO_SUPERUSER_USERNAME": "hari",
    "DJANGO_SUPERUSER_PASSWORD": "a-long-enough-password",
    "DJANGO_SUPERUSER_EMAIL": "hari646592@gmail.com",
}


@pytest.fixture
def credentials(monkeypatch):
    for key, value in CREDENTIALS.items():
        monkeypatch.setenv(key, value)
    return CREDENTIALS


@pytest.mark.django_db
class TestEnsureSuperuser:
    def test_creates_the_user(self, credentials):
        call_command("ensure_superuser", verbosity=0)

        user = User.objects.get(username="hari")
        assert user.is_superuser
        assert user.is_staff
        assert user.email == "hari646592@gmail.com"
        assert user.check_password("a-long-enough-password")

    def test_is_idempotent(self, credentials):
        call_command("ensure_superuser", verbosity=0)
        call_command("ensure_superuser", verbosity=0)
        assert User.objects.filter(username="hari").count() == 1

    def test_does_nothing_without_credentials(self, monkeypatch):
        monkeypatch.delenv("DJANGO_SUPERUSER_USERNAME", raising=False)
        monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)

        call_command("ensure_superuser", verbosity=0)
        assert not User.objects.exists()

    @pytest.mark.parametrize("missing", ["DJANGO_SUPERUSER_USERNAME", "DJANGO_SUPERUSER_PASSWORD"])
    def test_requires_both_username_and_password(self, credentials, monkeypatch, missing):
        monkeypatch.delenv(missing)
        call_command("ensure_superuser", verbosity=0)
        assert not User.objects.exists()

    def test_ignores_a_blank_username(self, credentials, monkeypatch):
        monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "   ")
        call_command("ensure_superuser", verbosity=0)
        assert not User.objects.exists()

    def test_rotating_the_password_takes_effect(self, credentials, monkeypatch):
        call_command("ensure_superuser", verbosity=0)

        monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "a-brand-new-password")
        call_command("ensure_superuser", verbosity=0)

        user = User.objects.get(username="hari")
        assert user.check_password("a-brand-new-password")
        assert not user.check_password("a-long-enough-password")

    def test_skip_password_update_leaves_the_password(self, credentials, monkeypatch):
        call_command("ensure_superuser", verbosity=0)

        monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "a-brand-new-password")
        call_command("ensure_superuser", "--skip-password-update", verbosity=0)

        assert User.objects.get(username="hari").check_password("a-long-enough-password")

    def test_restores_revoked_admin_privileges(self, credentials):
        call_command("ensure_superuser", verbosity=0)
        User.objects.filter(username="hari").update(is_staff=False, is_superuser=False)

        call_command("ensure_superuser", verbosity=0)

        user = User.objects.get(username="hari")
        assert user.is_staff
        assert user.is_superuser

    def test_updates_a_changed_email(self, credentials, monkeypatch):
        call_command("ensure_superuser", verbosity=0)

        monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "new@example.com")
        call_command("ensure_superuser", verbosity=0)

        assert User.objects.get(username="hari").email == "new@example.com"

    def test_adopts_a_preexisting_plain_user(self, credentials):
        """A non-admin account with that username is promoted, not duplicated."""
        User.objects.create_user(username="hari", password="whatever")

        call_command("ensure_superuser", verbosity=0)

        assert User.objects.filter(username="hari").count() == 1
        user = User.objects.get(username="hari")
        assert user.is_superuser
        assert user.check_password("a-long-enough-password")


@pytest.mark.django_db
class TestSeedPortfolioBootstrapsTheAdmin:
    """The deploy start command runs seed_portfolio, so it must create the admin.

    This is what makes the admin account appear on a host whose start command
    cannot be changed without re-syncing its config.
    """

    def test_seed_creates_the_superuser(self, credentials):
        call_command("seed_portfolio", verbosity=0)
        user = User.objects.get(username="hari")
        assert user.is_superuser
        assert user.check_password("a-long-enough-password")

    def test_seed_without_credentials_creates_no_user(self, monkeypatch):
        monkeypatch.delenv("DJANGO_SUPERUSER_USERNAME", raising=False)
        monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
        call_command("seed_portfolio", verbosity=0)
        assert not User.objects.exists()

    def test_skip_superuser_flag_is_honoured(self, credentials):
        call_command("seed_portfolio", "--skip-superuser", verbosity=0)
        assert not User.objects.exists()

    def test_reset_still_bootstraps_the_admin(self, credentials):
        call_command("seed_portfolio", verbosity=0)
        call_command("seed_portfolio", "--reset", verbosity=0)
        assert User.objects.get(username="hari").is_superuser

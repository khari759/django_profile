"""Tests for the MAILERS mapping.

A wrong mapping fails silently — Django reads only BACKEND and OPTIONS from a
mailer config, so misplaced keys are ignored and mail never sends. These tests
assert the shape Django actually consumes, and that a real connection object
ends up with the configured credentials.
"""

import pytest
from django.core.mail import mailers
from django.test import override_settings

from config.email import CONSOLE_BACKEND, SMTP_BACKEND, build_mailers

SMTP_ENV = {
    "DJANGO_EMAIL_BACKEND": SMTP_BACKEND,
    "DJANGO_EMAIL_HOST": "smtp.gmail.com",
    "DJANGO_EMAIL_PORT": "587",
    "DJANGO_EMAIL_USER": "hari646592@gmail.com",
    "DJANGO_EMAIL_PASSWORD": "app-specific-password",
    "DJANGO_EMAIL_USE_TLS": "True",
}


class TestBackendSelection:
    def test_console_backend_in_debug(self):
        assert build_mailers({}, debug=True)["default"]["BACKEND"] == CONSOLE_BACKEND

    def test_smtp_backend_in_production(self):
        assert build_mailers({}, debug=False)["default"]["BACKEND"] == SMTP_BACKEND

    def test_explicit_backend_wins(self):
        env = {"DJANGO_EMAIL_BACKEND": CONSOLE_BACKEND}
        assert build_mailers(env, debug=False)["default"]["BACKEND"] == CONSOLE_BACKEND

    def test_blank_backend_is_ignored(self):
        # An unset host variable arrives as "", which must not select a
        # nonexistent backend.
        env = {"DJANGO_EMAIL_BACKEND": ""}
        assert build_mailers(env, debug=False)["default"]["BACKEND"] == SMTP_BACKEND


class TestSmtpOptions:
    def test_connection_settings_live_under_options(self):
        """The regression this file exists for: keys must be inside OPTIONS."""
        mailer = build_mailers(SMTP_ENV, debug=False)["default"]

        assert "OPTIONS" in mailer, "connection settings must be nested under OPTIONS"
        assert set(mailer) == {"BACKEND", "OPTIONS"}, (
            "Django ignores any other top-level key, so nothing else belongs here"
        )

    def test_options_use_the_backend_argument_names(self):
        options = build_mailers(SMTP_ENV, debug=False)["default"]["OPTIONS"]

        assert options["host"] == "smtp.gmail.com"
        assert options["port"] == 587
        assert options["username"] == "hari646592@gmail.com"
        assert options["password"] == "app-specific-password"
        assert options["use_tls"] is True
        assert options["use_ssl"] is False

    def test_tls_is_on_by_default(self):
        options = build_mailers({}, debug=False)["default"]["OPTIONS"]
        assert options["use_tls"] is True
        assert options["port"] == 587

    def test_ssl_mode_disables_tls_and_uses_port_465(self):
        # The SMTP backend refuses to start with both TLS and SSL enabled.
        env = {"DJANGO_EMAIL_USE_SSL": "true"}
        options = build_mailers(env, debug=False)["default"]["OPTIONS"]
        assert options["use_ssl"] is True
        assert options["use_tls"] is False
        assert options["port"] == 465

    def test_explicit_port_overrides_the_default(self):
        options = build_mailers({"DJANGO_EMAIL_PORT": "2525"}, debug=False)["default"]["OPTIONS"]
        assert options["port"] == 2525

    def test_non_numeric_port_falls_back(self):
        options = build_mailers({"DJANGO_EMAIL_PORT": "not-a-port"}, debug=False)["default"][
            "OPTIONS"
        ]
        assert options["port"] == 587

    def test_console_backend_gets_no_connection_options(self):
        # Backends reject arguments they do not accept, so OPTIONS must be
        # omitted for anything other than SMTP.
        mailer = build_mailers({"DJANGO_EMAIL_BACKEND": CONSOLE_BACKEND}, debug=False)["default"]
        assert "OPTIONS" not in mailer


class TestDjangoAcceptsTheConfig:
    """Build a real connection from the config, proving Django applies it."""

    def test_smtp_connection_receives_the_credentials(self):
        with override_settings(MAILERS=build_mailers(SMTP_ENV, debug=False)):
            connection = mailers["default"]

        assert connection.host == "smtp.gmail.com"
        assert connection.port == 587
        assert connection.username == "hari646592@gmail.com"
        assert connection.password == "app-specific-password"
        assert connection.use_tls is True

    def test_console_connection_builds(self):
        with override_settings(
            MAILERS=build_mailers({"DJANGO_EMAIL_BACKEND": CONSOLE_BACKEND}, debug=True)
        ):
            connection = mailers["default"]

        assert connection.__class__.__module__.endswith("console")

    @pytest.mark.django_db
    def test_contact_form_sends_through_the_configured_mailer(self, api_client, settings):
        """End to end: a submission reaches the mailer Django has configured."""
        from django.core import mail
        from django.urls import reverse

        settings.CONTACT_NOTIFY_EMAIL = "owner@example.com"
        response = api_client.post(
            reverse("portfolio:contact"),
            {
                "name": "Recruiter",
                "email": "recruiter@example.com",
                "subject": "Role",
                "message": "We would like to talk to you about a role.",
            },
            format="json",
        )

        assert response.status_code == 201
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["owner@example.com"]

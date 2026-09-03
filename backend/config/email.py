"""Builds Django's MAILERS setting from environment variables.

Kept out of settings.py so the mapping can be unit tested. Getting it wrong is
silent: Django 6.1 reads only "BACKEND" and "OPTIONS" from a mailer config, so
misplaced connection keys are ignored rather than rejected, and mail simply
never sends.
"""

SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
CONSOLE_BACKEND = "django.core.mail.backends.console.EmailBackend"


def _as_bool(value, default=False):
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_mailers(env, debug):
    """Return a MAILERS dict for the given environment mapping.

    Console output in development, SMTP in production, overridable with
    DJANGO_EMAIL_BACKEND. OPTIONS are only attached for the SMTP backend
    because other backends reject connection arguments they do not accept.
    """
    backend = env.get("DJANGO_EMAIL_BACKEND") or (CONSOLE_BACKEND if debug else SMTP_BACKEND)

    mailer = {"BACKEND": backend}

    if backend == SMTP_BACKEND:
        use_ssl = _as_bool(env.get("DJANGO_EMAIL_USE_SSL"))
        # TLS is the common case (port 587); SSL (465) is the alternative, and
        # the SMTP backend rejects both being enabled at once.
        use_tls = False if use_ssl else _as_bool(env.get("DJANGO_EMAIL_USE_TLS"), True)
        mailer["OPTIONS"] = {
            "host": env.get("DJANGO_EMAIL_HOST", "localhost"),
            "port": _as_int(env.get("DJANGO_EMAIL_PORT"), 465 if use_ssl else 587),
            "username": env.get("DJANGO_EMAIL_USER", ""),
            "password": env.get("DJANGO_EMAIL_PASSWORD", ""),
            "use_tls": use_tls,
            "use_ssl": use_ssl,
            "timeout": _as_int(env.get("DJANGO_EMAIL_TIMEOUT"), 10),
        }

    return {"default": mailer}

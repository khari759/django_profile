"""Create the admin user from environment variables, idempotently.

Django's own `createsuperuser --noinput` errors when the user already exists,
so it cannot run on every boot. This command can: it creates the account when
missing, keeps it in sync when present, and does nothing at all when the
environment variables are unset.

That matters on hosts with ephemeral or expiring databases (Render's free
PostgreSQL is dropped after 30 days), where the admin account would otherwise
have to be recreated by hand after every rebuild.

Reads:
    DJANGO_SUPERUSER_USERNAME   (required to do anything)
    DJANGO_SUPERUSER_PASSWORD   (required to do anything)
    DJANGO_SUPERUSER_EMAIL      (optional)
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the admin superuser from DJANGO_SUPERUSER_* env vars."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-password-update",
            action="store_true",
            help="Leave an existing user's password alone.",
        )

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()

        if not username or not password:
            # Not an error: local development creates the user interactively.
            self.stdout.write("  superuser: DJANGO_SUPERUSER_USERNAME/PASSWORD not set, skipping")
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            **{User.USERNAME_FIELD: username},
            defaults={"is_staff": True, "is_superuser": True},
        )

        if created:
            user.email = email
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"  superuser: created '{username}'"))
            return

        # The user exists. Re-assert admin rights in case they were revoked,
        # and re-apply the password so rotating the env var actually works.
        changes = []
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            changes.append("privileges")
        if email and user.email != email:
            user.email = email
            changes.append("email")
        if not options["skip_password_update"] and not user.check_password(password):
            user.set_password(password)
            changes.append("password")

        if changes:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"  superuser: updated '{username}' ({', '.join(changes)})")
            )
        else:
            self.stdout.write(f"  superuser: '{username}' already up to date")

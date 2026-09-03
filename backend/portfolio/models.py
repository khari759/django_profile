"""Content models for the portfolio site.

Everything the public site renders is editable from the Django admin, so
updating the portfolio never requires a redeploy.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def unique_slug(instance, value, max_length):
    """Slugify `value`, appending `-2`, `-3`, … until the slug is free.

    Needed because distinct names can collapse to the same slug — slugify
    strips punctuation, so "C" and "C++" both yield "c".
    """
    base = slugify(value)[:max_length] or "item"
    model = instance.__class__
    candidate = base
    suffix = 1
    while model._default_manager.filter(slug=candidate).exclude(pk=instance.pk).exists():
        suffix += 1
        tail = f"-{suffix}"
        candidate = f"{base[: max_length - len(tail)]}{tail}"
    return candidate


class TimeStampedModel(models.Model):
    """Adds created/updated bookkeeping to every content model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    """Site owner details. Only one row is allowed."""

    full_name = models.CharField(max_length=120)
    headline = models.CharField(
        max_length=200,
        help_text="Short role line, e.g. 'Full Stack Software Engineer'.",
    )
    summary = models.TextField(help_text="Professional summary shown in the About section.")
    location = models.CharField(max_length=120, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    years_of_experience = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        help_text="Displayed on the hero stats strip.",
    )
    avatar = models.ImageField(upload_to="profile/", blank=True, null=True)
    resume = models.FileField(
        upload_to="resume/",
        blank=True,
        null=True,
        help_text="PDF offered by the 'Download CV' button.",
    )
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    is_available_for_work = models.BooleanField(default=True)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profile"

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        """Enforce the singleton at the form/admin layer."""
        if Profile.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Only one Profile may exist. Edit the existing one instead.")


class SkillCategory(models.Model):
    """Grouping for skills, e.g. 'Languages', 'Backend', 'Databases'."""

    name = models.CharField(max_length=80, unique=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "skill categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        ("familiar", "Familiar"),
        ("proficient", "Proficient"),
        ("advanced", "Advanced"),
    ]

    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=80)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default="proficient")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_skill_per_category")
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Experience(TimeStampedModel):
    """A role held at a company."""

    company = models.CharField(max_length=140)
    role = models.CharField(max_length=140)
    location = models.CharField(max_length=120, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(
        blank=True, null=True, help_text="Leave empty for the current role."
    )
    is_current = models.BooleanField(default=False)
    company_url = models.URLField(blank=True)
    tech_summary = models.CharField(
        max_length=255, blank=True, help_text="Comma-separated stack used in this role."
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-start_date"]
        verbose_name_plural = "experience"

    def __str__(self):
        return f"{self.role} at {self.company}"

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before the start date."})
        if self.is_current and self.end_date:
            raise ValidationError({"end_date": "A current role must not have an end date."})

    @property
    def tech_list(self):
        return [item.strip() for item in self.tech_summary.split(",") if item.strip()]


class ExperienceHighlight(models.Model):
    """One achievement bullet under a role."""

    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name="highlights")
    text = models.TextField()
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.text[:60]


class Technology(models.Model):
    """A tag attachable to projects, e.g. 'Django', 'React'."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "technologies"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name, 70)
        return super().save(*args, **kwargs)


class Project(TimeStampedModel):
    """A portfolio piece shown in the Projects grid."""

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    summary = models.CharField(max_length=280, help_text="One-line pitch for the card.")
    description = models.TextField(help_text="Longer write-up shown in the detail view.")
    role = models.CharField(max_length=120, blank=True)
    technologies = models.ManyToManyField(Technology, related_name="projects", blank=True)
    thumbnail = models.ImageField(upload_to="projects/", blank=True, null=True)
    repo_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    started_on = models.DateField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title, 180)
        return super().save(*args, **kwargs)


class Education(TimeStampedModel):
    degree = models.CharField(max_length=180)
    institution = models.CharField(max_length=180)
    location = models.CharField(max_length=120, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-start_year"]
        verbose_name_plural = "education"

    def __str__(self):
        return f"{self.degree} — {self.institution}"

    def clean(self):
        if self.end_year and self.end_year < self.start_year:
            raise ValidationError({"end_year": "End year cannot be before the start year."})


class Certification(TimeStampedModel):
    name = models.CharField(max_length=180)
    issuer = models.CharField(max_length=180)
    issued_on = models.DateField(blank=True, null=True)
    credential_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-issued_on"]

    def __str__(self):
        return f"{self.name} — {self.issuer}"


class ContactMessage(models.Model):
    """A submission from the public contact form."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=180, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"

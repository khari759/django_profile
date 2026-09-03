"""Admin configuration — this is the CMS for the portfolio site."""

from django.contrib import admin
from django.utils.html import format_html

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

admin.site.site_header = "Portfolio administration"
admin.site.site_title = "Portfolio admin"
admin.site.index_title = "Manage portfolio content"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "headline", "email", "is_available_for_work"]
    fieldsets = [
        ("Identity", {"fields": ["full_name", "headline", "location", "avatar"]}),
        ("About", {"fields": ["summary", "years_of_experience", "is_available_for_work"]}),
        ("Contact", {"fields": ["email", "phone"]}),
        ("Links", {"fields": ["github_url", "linkedin_url", "website_url", "resume"]}),
    ]

    def has_add_permission(self, request):
        """Profile is a singleton — hide 'Add' once a row exists."""
        return not Profile.objects.exists()


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 3


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "display_order", "skill_count"]
    list_editable = ["display_order"]
    inlines = [SkillInline]

    @admin.display(description="Skills")
    def skill_count(self, obj):
        return obj.skills.count()


class ExperienceHighlightInline(admin.TabularInline):
    model = ExperienceHighlight
    extra = 3


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["role", "company", "start_date", "end_date", "is_current"]
    list_filter = ["is_current", "company"]
    search_fields = ["role", "company", "tech_summary"]
    inlines = [ExperienceHighlightInline]


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "project_count"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]

    @admin.display(description="Projects")
    def project_count(self, obj):
        return obj.projects.count()


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "is_featured", "is_published", "display_order", "links"]
    list_editable = ["is_featured", "is_published", "display_order"]
    list_filter = ["is_featured", "is_published", "technologies"]
    search_fields = ["title", "summary", "description"]
    prepopulated_fields = {"slug": ["title"]}
    filter_horizontal = ["technologies"]
    fieldsets = [
        (None, {"fields": ["title", "slug", "summary", "role", "started_on"]}),
        ("Content", {"fields": ["description", "thumbnail", "technologies"]}),
        ("Links", {"fields": ["repo_url", "live_url"]}),
        ("Visibility", {"fields": ["is_featured", "is_published", "display_order"]}),
    ]

    @admin.display(description="Links")
    def links(self, obj):
        parts = []
        if obj.repo_url:
            parts.append(format_html('<a href="{}" target="_blank">code</a>', obj.repo_url))
        if obj.live_url:
            parts.append(format_html('<a href="{}" target="_blank">live</a>', obj.live_url))
        return format_html(" · ".join(["{}"] * len(parts)), *parts) if parts else "—"


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["degree", "institution", "start_year", "end_year"]


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ["name", "issuer", "issued_on"]
    search_fields = ["name", "issuer"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "created_at", "is_read"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["name", "email", "subject", "message", "created_at"]
    actions = ["mark_as_read"]

    def has_add_permission(self, request):
        """Messages arrive through the public API, never by hand."""
        return False

    @admin.action(description="Mark selected messages as read")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} message(s) marked as read.")

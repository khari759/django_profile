from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("overview/", views.OverviewView.as_view(), name="overview"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("skills/", views.SkillCategoryListView.as_view(), name="skills"),
    path("experience/", views.ExperienceListView.as_view(), name="experience"),
    path("projects/", views.ProjectListView.as_view(), name="project-list"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("education/", views.EducationListView.as_view(), name="education"),
    path("certifications/", views.CertificationListView.as_view(), name="certifications"),
    path("contact/", views.ContactMessageCreateView.as_view(), name="contact"),
]

"""Seed the database with the site owner's real content.

Idempotent: safe to re-run. Use `--reset` to wipe content models first.
Edit the data below (or the Django admin) to keep the portfolio current.
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

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

PROFILE = {
    "full_name": "Hari Krishna Komire",
    "headline": "Full Stack Software Engineer — Python · Django · React · TypeScript",
    "summary": (
        "Full Stack Software Engineer with approximately 4 years of professional software "
        "development experience designing and developing web applications across frontend "
        "and backend technologies. Strong experience with Python, Django, TypeScript, "
        "JavaScript, React.js, PHP, Laravel, RESTful APIs, PostgreSQL, MySQL and MongoDB. "
        "Experienced in API integration, responsive web development, database-driven "
        "applications, and maintainable software design using object-oriented programming "
        "and SOLID principles. Currently expanding into AI-powered application development "
        "on top of a strong full-stack engineering foundation."
    ),
    "location": "Bengaluru, Karnataka, India",
    "email": "hari646592@gmail.com",
    "phone": "+91 70131 12432",
    "years_of_experience": 4,
    "github_url": "https://github.com/khari759",
    "linkedin_url": "https://linkedin.com/in/hari-krishna-komire/",
    "is_available_for_work": True,
}

SKILLS = [
    ("Languages", ["Python", "TypeScript", "JavaScript (ES6+)", "PHP", "SQL", "HTML5", "CSS3"]),
    ("Frontend", ["React.js", "Next.js", "Redux", "Responsive Design"]),
    ("Backend", ["Django", "Django REST Framework", "Flask", "Laravel", "RESTful APIs"]),
    ("Databases", ["PostgreSQL", "MySQL", "MongoDB"]),
    (
        "Engineering",
        [
            "API Integration",
            "Object-Oriented Programming",
            "SOLID Principles",
            "MVT Architecture",
            "System Integration",
        ],
    ),
    ("Tools & Platforms", ["Git", "GitHub", "GitLab CI/CD", "Docker", "Linux (Ubuntu)"]),
]

EXPERIENCE = [
    {
        "company": "Infanion Software Solutions Private Ltd.",
        "role": "Associate Software Developer",
        "location": "Bengaluru, India",
        "start_date": date(2023, 3, 1),
        "end_date": None,
        "is_current": True,
        "tech_summary": "Python, Django, TypeScript, React.js, PostgreSQL, Drupal, Laravel",
        "display_order": 0,
        "highlights": [
            "Develop and maintain web applications using Python, Django, TypeScript, "
            "React.js, PostgreSQL, Drupal and Laravel.",
            "Build and maintain backend functionality and RESTful APIs supporting "
            "application workflows and system integrations.",
            "Develop responsive frontend interfaces using React.js, TypeScript, "
            "JavaScript, HTML and CSS.",
            "Work with PostgreSQL and other databases to support application data "
            "management and business functionality.",
            "Apply object-oriented programming and SOLID design principles to improve "
            "code maintainability, scalability and robustness.",
            "Collaborate with cross-functional teams to analyse requirements, troubleshoot "
            "application issues and deliver features.",
            "Work with Git-based development workflows, Linux environments and CI/CD processes.",
        ],
    },
    {
        "company": "Infanion Software Solutions Private Ltd.",
        "role": "Trainee Software Developer",
        "location": "Bengaluru, India",
        "start_date": date(2022, 9, 1),
        "end_date": date(2023, 3, 1),
        "is_current": False,
        "tech_summary": "PHP, JavaScript, CSS, Drupal, Django REST Framework",
        "display_order": 1,
        "highlights": [
            "Designed and developed responsive web applications using PHP, JavaScript, "
            "CSS and Drupal.",
            "Built and integrated RESTful APIs using Django REST Framework to support "
            "application and system integration.",
            "Gained hands-on experience in backend development, frontend development, "
            "database integration, debugging and application support.",
        ],
    },
    {
        "company": "Sri Punyabhoomi Developers Pvt. Ltd.",
        "role": "Civil Engineer",
        "location": "Hyderabad, India",
        "start_date": date(2019, 8, 1),
        "end_date": date(2022, 8, 1),
        "is_current": False,
        "tech_summary": "Project scheduling, Critical path analysis",
        "display_order": 2,
        "highlights": [
            "Performed project scheduling and critical path analysis, and coordinated work "
            "assignments based on project schedules.",
            "Prepared monthly invoices and coordinated client certification processes for "
            "payment release.",
        ],
    },
]

PROJECTS = [
    {
        "title": "AbsoluteCORE — Payroll Management Application",
        "summary": (
            "Enterprise payroll platform handling contracts, payslips, attendance and "
            "document workflows for employers and employees."
        ),
        "description": (
            "Contributed to the development of a payroll management application supporting "
            "enterprise payroll workflows.\n\n"
            "Built application features using Python, Django, TypeScript, Redux and "
            "PostgreSQL, including role-based user interfaces and personalised dashboards "
            "for employers and employees. Supported application workflows related to "
            "contracts, payslips, attendance and document management, and integrated "
            "external APIs — including Bright Staffing — to keep data synchronised between "
            "systems. Also contributed to the responsive user interfaces and the backend "
            "application functionality behind them."
        ),
        "role": "Developer",
        "technologies": ["Python", "Django", "TypeScript", "Redux", "PostgreSQL"],
        "is_featured": True,
        "display_order": 0,
    },
    {
        "title": "Developer Portfolio Platform",
        "summary": (
            "This site: a Django REST Framework API with an admin CMS, paired with a "
            "React + TypeScript single-page frontend."
        ),
        "description": (
            "A portfolio platform built to be maintained rather than rewritten. Every "
            "section on the public site — profile, skills, experience, projects, education "
            "and certifications — is a Django model editable from the admin, so content "
            "changes never require a redeploy.\n\n"
            "The backend exposes a read-only JSON API plus a rate-limited contact endpoint "
            "that persists messages and emails a notification. The frontend is a React 19 "
            "single-page app in TypeScript, built with Vite, that fetches the whole page "
            "payload from one aggregate `/api/overview/` endpoint. Ships with pytest and "
            "Vitest suites, Docker Compose for a PostgreSQL-backed stack, and a GitHub "
            "Actions pipeline running lint and tests on both halves."
        ),
        "role": "Designer & Developer",
        "technologies": [
            "Python",
            "Django",
            "Django REST Framework",
            "React.js",
            "TypeScript",
            "PostgreSQL",
            "Docker",
            "Vite",
        ],
        "repo_url": "https://github.com/khari759/django_profile",
        "is_featured": True,
        "display_order": 1,
    },
    {
        "title": "Client Web Applications — Drupal & Laravel",
        "summary": (
            "Responsive client-facing web applications and CMS integrations delivered with "
            "PHP, Drupal and Laravel."
        ),
        "description": (
            "Designed and developed responsive web applications using PHP, JavaScript, CSS, "
            "Drupal and Laravel, and integrated RESTful APIs built with Django REST "
            "Framework to connect these applications with other systems. Work covered "
            "frontend templating, backend business logic, database integration, debugging "
            "and ongoing application support.\n\n"
            "Replace or expand this entry from the Django admin with the specific client "
            "projects you are able to describe publicly."
        ),
        "role": "Developer",
        "technologies": ["PHP", "Laravel", "Drupal", "JavaScript", "MySQL"],
        "is_featured": False,
        "display_order": 2,
    },
]

EDUCATION = [
    {
        "degree": "Bachelor of Technology (B.Tech) — Civil Engineering",
        "institution": "Annamacharya Institute of Technology and Sciences",
        "location": "Hyderabad, India",
        "start_year": 2015,
        "end_year": 2019,
        "notes": (
            "Transitioned from civil engineering into software development, bringing a "
            "planning-and-scheduling mindset to delivery work."
        ),
    }
]

CERTIFICATIONS = [
    {"name": "Associate Developer Certification", "issuer": "Boomi Education Services"},
    {
        "name": "Certificate in Python Programming",
        "issuer": "NxtWave Disruptive Technologies",
    },
]

CONTENT_MODELS = [
    ExperienceHighlight,
    Experience,
    Skill,
    SkillCategory,
    Project,
    Technology,
    Education,
    Certification,
    Profile,
]


class Command(BaseCommand):
    help = "Populate the database with portfolio content. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing portfolio content before seeding (keeps contact messages).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            for model in CONTENT_MODELS:
                model.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing portfolio content."))

        self._seed_profile()
        self._seed_skills()
        self._seed_experience()
        self._seed_projects()
        self._seed_education()
        self._seed_certifications()

        self.stdout.write(self.style.SUCCESS("Portfolio content seeded."))

    def _seed_profile(self):
        profile = Profile.objects.first()
        if profile is None:
            Profile.objects.create(**PROFILE)
            self.stdout.write("  profile: created")
            return
        for field, value in PROFILE.items():
            setattr(profile, field, value)
        profile.save()
        self.stdout.write("  profile: updated")

    def _seed_skills(self):
        for order, (category_name, skill_names) in enumerate(SKILLS):
            category, _ = SkillCategory.objects.update_or_create(
                name=category_name, defaults={"display_order": order}
            )
            for skill_order, skill_name in enumerate(skill_names):
                Skill.objects.update_or_create(
                    category=category,
                    name=skill_name,
                    defaults={"display_order": skill_order},
                )
        self.stdout.write(f"  skills: {Skill.objects.count()} across {len(SKILLS)} categories")

    def _seed_experience(self):
        for entry in EXPERIENCE:
            highlights = entry.pop("highlights")
            experience, _ = Experience.objects.update_or_create(
                company=entry["company"],
                role=entry["role"],
                start_date=entry["start_date"],
                defaults=entry,
            )
            experience.highlights.all().delete()
            ExperienceHighlight.objects.bulk_create(
                [
                    ExperienceHighlight(experience=experience, text=text, display_order=index)
                    for index, text in enumerate(highlights)
                ]
            )
            entry["highlights"] = highlights
        self.stdout.write(f"  experience: {Experience.objects.count()} roles")

    def _seed_projects(self):
        for entry in PROJECTS:
            tech_names = entry.pop("technologies")
            project, _ = Project.objects.update_or_create(title=entry["title"], defaults=entry)
            technologies = [Technology.objects.get_or_create(name=name)[0] for name in tech_names]
            project.technologies.set(technologies)
            entry["technologies"] = tech_names
        self.stdout.write(f"  projects: {Project.objects.count()}")

    def _seed_education(self):
        for entry in EDUCATION:
            Education.objects.update_or_create(
                degree=entry["degree"], institution=entry["institution"], defaults=entry
            )
        self.stdout.write(f"  education: {Education.objects.count()}")

    def _seed_certifications(self):
        for order, entry in enumerate(CERTIFICATIONS):
            Certification.objects.update_or_create(
                name=entry["name"],
                issuer=entry["issuer"],
                defaults={**entry, "display_order": order},
            )
        self.stdout.write(f"  certifications: {Certification.objects.count()}")

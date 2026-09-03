import type { Overview, Profile, Project } from "../types";

export const profileFixture: Profile = {
  full_name: "Hari Krishna Komire",
  headline: "Full Stack Software Engineer",
  summary: "First paragraph about me.\n\nSecond paragraph about me.",
  location: "Bengaluru, India",
  email: "hari646592@gmail.com",
  phone: "+91 70131 12432",
  years_of_experience: "4.0",
  avatar: null,
  resume: "/media/resume/cv.pdf",
  github_url: "https://github.com/example",
  linkedin_url: "https://linkedin.com/in/example",
  website_url: "",
  is_available_for_work: true,
};

export const projectsFixture: Project[] = [
  {
    id: 1,
    title: "AbsoluteCORE Payroll",
    slug: "absolutecore-payroll",
    summary: "Enterprise payroll platform.",
    description: "Payroll intro paragraph.\n\nPayroll detail paragraph.",
    role: "Developer",
    technologies: [
      { id: 1, name: "Django", slug: "django" },
      { id: 2, name: "PostgreSQL", slug: "postgresql" },
    ],
    thumbnail: null,
    repo_url: "https://github.com/example/payroll",
    live_url: "",
    is_featured: true,
    started_on: null,
  },
  {
    id: 2,
    title: "Portfolio Site",
    slug: "portfolio-site",
    summary: "This website.",
    description: "Built with Django and React.",
    role: "",
    technologies: [{ id: 3, name: "React.js", slug: "reactjs" }],
    thumbnail: null,
    repo_url: "",
    live_url: "https://example.com",
    is_featured: false,
    started_on: null,
  },
];

export const overviewFixture: Overview = {
  profile: profileFixture,
  skill_categories: [
    {
      id: 1,
      name: "Backend",
      skills: [
        { id: 1, name: "Django", proficiency: "advanced" },
        { id: 2, name: "Django REST Framework", proficiency: "proficient" },
      ],
    },
    {
      id: 2,
      name: "Frontend",
      skills: [{ id: 3, name: "React.js", proficiency: "proficient" }],
    },
  ],
  experience: [
    {
      id: 1,
      company: "Infanion Software Solutions Private Ltd.",
      company_url: "",
      role: "Associate Software Developer",
      location: "Bengaluru, India",
      start_date: "2023-03-01",
      end_date: null,
      is_current: true,
      tech_list: ["Python", "Django", "React.js"],
      highlights: [{ id: 1, text: "Built RESTful APIs with Django REST Framework." }],
    },
  ],
  projects: projectsFixture,
  education: [
    {
      id: 1,
      degree: "B.Tech Civil Engineering",
      institution: "Annamacharya Institute of Technology and Sciences",
      location: "Hyderabad, India",
      start_year: 2015,
      end_year: 2019,
      notes: "",
    },
  ],
  certifications: [
    {
      id: 1,
      name: "Associate Developer Certification",
      issuer: "Boomi Education Services",
      issued_on: null,
      credential_url: "",
    },
  ],
};

/** Builds a `fetch` stand-in that answers the overview and contact endpoints. */
export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

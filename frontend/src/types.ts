/** Types mirroring the Django REST Framework serializers in `backend/portfolio/serializers.py`. */

export type Proficiency = "familiar" | "proficient" | "advanced";

export interface Profile {
  full_name: string;
  headline: string;
  summary: string;
  location: string;
  email: string;
  phone: string;
  years_of_experience: string;
  avatar: string | null;
  resume: string | null;
  github_url: string;
  linkedin_url: string;
  website_url: string;
  is_available_for_work: boolean;
}

export interface Skill {
  id: number;
  name: string;
  proficiency: Proficiency;
}

export interface SkillCategory {
  id: number;
  name: string;
  skills: Skill[];
}

export interface ExperienceHighlight {
  id: number;
  text: string;
}

export interface Experience {
  id: number;
  company: string;
  company_url: string;
  role: string;
  location: string;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  tech_list: string[];
  highlights: ExperienceHighlight[];
}

export interface Technology {
  id: number;
  name: string;
  slug: string;
}

export interface Project {
  id: number;
  title: string;
  slug: string;
  summary: string;
  description: string;
  role: string;
  technologies: Technology[];
  thumbnail: string | null;
  repo_url: string;
  live_url: string;
  is_featured: boolean;
  started_on: string | null;
}

export interface Education {
  id: number;
  degree: string;
  institution: string;
  location: string;
  start_year: number;
  end_year: number | null;
  notes: string;
}

export interface Certification {
  id: number;
  name: string;
  issuer: string;
  issued_on: string | null;
  credential_url: string;
}

/** Payload of `GET /api/overview/` — everything the page renders, in one request. */
export interface Overview {
  profile: Profile | null;
  skill_categories: SkillCategory[];
  experience: Experience[];
  projects: Project[];
  education: Education[];
  certifications: Certification[];
}

export interface ContactPayload {
  name: string;
  email: string;
  subject: string;
  message: string;
}

/** DRF returns `{field: ["message", ...]}` for validation errors. */
export type FieldErrors = Partial<Record<keyof ContactPayload | "detail", string[]>>;

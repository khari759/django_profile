import { useMemo, useState } from "react";

import { ProjectDialog } from "./ProjectDialog";
import { Section } from "./Section";
import { mediaUrl } from "../api/client";
import type { Project } from "../types";

interface ProjectsProps {
  projects: Project[];
}

const ALL = "all";

export function Projects({ projects }: ProjectsProps) {
  const [activeTech, setActiveTech] = useState<string>(ALL);
  const [openProject, setOpenProject] = useState<Project | null>(null);

  // Filter options are derived from the projects themselves, so adding a
  // project in the admin automatically adds its technologies here.
  const filters = useMemo(() => {
    const counts = new Map<string, { name: string; count: number }>();
    for (const project of projects) {
      for (const tech of project.technologies) {
        const existing = counts.get(tech.slug);
        counts.set(tech.slug, {
          name: tech.name,
          count: (existing?.count ?? 0) + 1,
        });
      }
    }
    return [...counts.entries()]
      .map(([slug, value]) => ({ slug, ...value }))
      .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
  }, [projects]);

  const visibleProjects = useMemo(
    () =>
      activeTech === ALL
        ? projects
        : projects.filter((project) =>
            project.technologies.some((tech) => tech.slug === activeTech),
          ),
    [projects, activeTech],
  );

  if (projects.length === 0) return null;

  return (
    <Section
      id="projects"
      eyebrow="04 — Projects"
      title="Things I have built"
      description="Select a technology to filter, or open a project for the full write-up."
    >
      {filters.length > 1 ? (
        <div className="filters" role="group" aria-label="Filter projects by technology">
          <button
            type="button"
            className={`filter ${activeTech === ALL ? "filter--active" : ""}`}
            onClick={() => setActiveTech(ALL)}
            aria-pressed={activeTech === ALL}
          >
            All <span className="filter__count">{projects.length}</span>
          </button>
          {filters.map((filter) => (
            <button
              key={filter.slug}
              type="button"
              className={`filter ${activeTech === filter.slug ? "filter--active" : ""}`}
              onClick={() => setActiveTech(filter.slug)}
              aria-pressed={activeTech === filter.slug}
            >
              {filter.name} <span className="filter__count">{filter.count}</span>
            </button>
          ))}
        </div>
      ) : null}

      <div className="projects" aria-live="polite">
        {visibleProjects.map((project) => {
          const thumbnail = mediaUrl(project.thumbnail);
          return (
            <article className="card project" key={project.id}>
              {thumbnail ? (
                <img
                  className="project__thumb"
                  src={thumbnail}
                  alt={`${project.title} preview`}
                  loading="lazy"
                />
              ) : (
                <div className="project__thumb project__thumb--placeholder" aria-hidden="true">
                  {project.title.slice(0, 1)}
                </div>
              )}

              <div className="project__body">
                <div className="project__title-row">
                  <h3 className="project__title">{project.title}</h3>
                  {project.is_featured ? (
                    <span className="badge badge--featured">Featured</span>
                  ) : null}
                </div>
                <p className="project__summary">{project.summary}</p>

                <ul className="chips chips--muted">
                  {project.technologies.map((tech) => (
                    <li className="chip" key={tech.id}>
                      {tech.name}
                    </li>
                  ))}
                </ul>

                <div className="project__actions">
                  <button
                    type="button"
                    className="button button--small"
                    onClick={() => setOpenProject(project)}
                  >
                    Read more
                  </button>
                  {project.repo_url ? (
                    <a
                      className="button button--small button--ghost"
                      href={project.repo_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Code
                    </a>
                  ) : null}
                  {project.live_url ? (
                    <a
                      className="button button--small button--ghost"
                      href={project.live_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Live
                    </a>
                  ) : null}
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {visibleProjects.length === 0 ? (
        <p className="empty">No projects use that technology yet.</p>
      ) : null}

      {openProject ? (
        <ProjectDialog project={openProject} onClose={() => setOpenProject(null)} />
      ) : null}
    </Section>
  );
}

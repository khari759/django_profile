import { Section } from "./Section";
import { formatDateRange, formatDuration } from "../utils/dates";
import type { Experience } from "../types";

interface ExperienceTimelineProps {
  roles: Experience[];
}

export function ExperienceTimeline({ roles }: ExperienceTimelineProps) {
  if (roles.length === 0) return null;

  return (
    <Section
      id="experience"
      eyebrow="03 — Experience"
      title="Where I have worked"
      description="Most recent first."
    >
      <ol className="timeline">
        {roles.map((role) => (
          <li className="timeline__item" key={role.id}>
            <div className="timeline__marker" aria-hidden="true" />
            <article className="card timeline__card">
              <header className="timeline__header">
                <div>
                  <h3 className="timeline__role">{role.role}</h3>
                  <p className="timeline__company">
                    {role.company_url ? (
                      <a href={role.company_url} target="_blank" rel="noreferrer">
                        {role.company}
                      </a>
                    ) : (
                      role.company
                    )}
                    {role.location ? <span> · {role.location}</span> : null}
                  </p>
                </div>
                <p className="timeline__dates">
                  <span>{formatDateRange(role.start_date, role.end_date)}</span>
                  <span className="timeline__duration">
                    {formatDuration(role.start_date, role.end_date)}
                  </span>
                  {role.is_current ? <span className="badge badge--current">Current</span> : null}
                </p>
              </header>

              {role.highlights.length > 0 ? (
                <ul className="timeline__highlights">
                  {role.highlights.map((highlight) => (
                    <li key={highlight.id}>{highlight.text}</li>
                  ))}
                </ul>
              ) : null}

              {role.tech_list.length > 0 ? (
                <ul className="chips chips--muted">
                  {role.tech_list.map((tech) => (
                    <li className="chip" key={tech}>
                      {tech}
                    </li>
                  ))}
                </ul>
              ) : null}
            </article>
          </li>
        ))}
      </ol>
    </Section>
  );
}

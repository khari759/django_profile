import { Section } from "./Section";
import { formatMonthYear } from "../utils/dates";
import type { Certification, Education } from "../types";

interface CredentialsProps {
  education: Education[];
  certifications: Certification[];
}

export function Credentials({ education, certifications }: CredentialsProps) {
  if (education.length === 0 && certifications.length === 0) return null;

  return (
    <Section id="credentials" eyebrow="05 — Credentials" title="Education & certifications">
      <div className="credentials">
        {education.length > 0 ? (
          <div className="credentials__column">
            <h3 className="credentials__heading">Education</h3>
            {education.map((entry) => (
              <article className="card credentials__card" key={entry.id}>
                <h4 className="credentials__title">{entry.degree}</h4>
                <p className="credentials__meta">
                  {entry.institution}
                  {entry.location ? ` · ${entry.location}` : ""}
                </p>
                <p className="credentials__dates">
                  {entry.start_year} — {entry.end_year ?? "Present"}
                </p>
                {entry.notes ? <p className="credentials__notes">{entry.notes}</p> : null}
              </article>
            ))}
          </div>
        ) : null}

        {certifications.length > 0 ? (
          <div className="credentials__column">
            <h3 className="credentials__heading">Certifications</h3>
            {certifications.map((entry) => (
              <article className="card credentials__card" key={entry.id}>
                <h4 className="credentials__title">
                  {entry.credential_url ? (
                    <a href={entry.credential_url} target="_blank" rel="noreferrer">
                      {entry.name}
                    </a>
                  ) : (
                    entry.name
                  )}
                </h4>
                <p className="credentials__meta">{entry.issuer}</p>
                {entry.issued_on ? (
                  <p className="credentials__dates">{formatMonthYear(entry.issued_on)}</p>
                ) : null}
              </article>
            ))}
          </div>
        ) : null}
      </div>
    </Section>
  );
}

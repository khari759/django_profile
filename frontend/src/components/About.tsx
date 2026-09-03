import { Section } from "./Section";
import type { Profile } from "../types";

interface AboutProps {
  profile: Profile;
  topSkills: string[];
}

export function About({ profile, topSkills }: AboutProps) {
  const paragraphs = profile.summary.split(/\n{2,}/).filter(Boolean);

  return (
    <Section id="about" eyebrow="01 — About" title="A bit about me">
      <div className="about">
        <div className="about__prose">
          {paragraphs.map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>

        <aside className="about__card" aria-label="Quick facts">
          <dl className="facts">
            {profile.location ? (
              <div className="facts__row">
                <dt>Based in</dt>
                <dd>{profile.location}</dd>
              </div>
            ) : null}
            <div className="facts__row">
              <dt>Email</dt>
              <dd>
                <a href={`mailto:${profile.email}`}>{profile.email}</a>
              </dd>
            </div>
            {profile.phone ? (
              <div className="facts__row">
                <dt>Phone</dt>
                <dd>
                  <a href={`tel:${profile.phone.replace(/\s/g, "")}`}>{profile.phone}</a>
                </dd>
              </div>
            ) : null}
            <div className="facts__row">
              <dt>Status</dt>
              <dd>
                {profile.is_available_for_work
                  ? "Open to new opportunities"
                  : "Currently engaged"}
              </dd>
            </div>
          </dl>

          {topSkills.length > 0 ? (
            <>
              <p className="about__card-label">Core stack</p>
              <ul className="chips">
                {topSkills.map((skill) => (
                  <li className="chip" key={skill}>
                    {skill}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
        </aside>
      </div>
    </Section>
  );
}

import { mediaUrl } from "../api/client";
import type { Profile } from "../types";

interface HeroProps {
  profile: Profile;
  projectCount: number;
  skillCount: number;
}

export function Hero({ profile, projectCount, skillCount }: HeroProps) {
  const avatar = mediaUrl(profile.avatar);
  const resume = mediaUrl(profile.resume);
  const years = Number(profile.years_of_experience);

  return (
    <section className="hero" id="top" aria-label="Introduction">
      <div className="hero__glow" aria-hidden="true" />
      <div className="hero__content">
        {profile.is_available_for_work ? (
          <p className="badge badge--available">
            <span className="badge__dot" aria-hidden="true" />
            Open to new opportunities
          </p>
        ) : null}

        <h1 className="hero__name">{profile.full_name}</h1>
        <p className="hero__headline">{profile.headline}</p>
        {profile.location ? <p className="hero__location">📍 {profile.location}</p> : null}

        <div className="hero__actions">
          <a className="button button--primary" href="#projects">
            View my work
          </a>
          {resume ? (
            <a className="button button--ghost" href={resume} target="_blank" rel="noreferrer">
              Download CV
            </a>
          ) : null}
          <a className="button button--ghost" href="#contact">
            Get in touch
          </a>
        </div>

        <ul className="hero__stats">
          {years > 0 ? (
            <li className="stat">
              <span className="stat__value">{years}+</span>
              <span className="stat__label">Years building software</span>
            </li>
          ) : null}
          <li className="stat">
            <span className="stat__value">{projectCount}</span>
            <span className="stat__label">Projects shipped</span>
          </li>
          <li className="stat">
            <span className="stat__value">{skillCount}</span>
            <span className="stat__label">Tools &amp; technologies</span>
          </li>
        </ul>

        <div className="hero__links">
          {profile.github_url ? (
            <a href={profile.github_url} target="_blank" rel="noreferrer">
              GitHub
            </a>
          ) : null}
          {profile.linkedin_url ? (
            <a href={profile.linkedin_url} target="_blank" rel="noreferrer">
              LinkedIn
            </a>
          ) : null}
          {profile.email ? <a href={`mailto:${profile.email}`}>Email</a> : null}
        </div>
      </div>

      {avatar ? (
        <div className="hero__portrait">
          <img src={avatar} alt={`Portrait of ${profile.full_name}`} />
        </div>
      ) : null}
    </section>
  );
}

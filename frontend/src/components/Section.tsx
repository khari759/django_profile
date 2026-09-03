import type { ReactNode } from "react";

interface SectionProps {
  id: string;
  eyebrow: string;
  title: string;
  description?: string;
  children: ReactNode;
}

/** Shared section shell: anchor target, heading block, and content slot. */
export function Section({ id, eyebrow, title, description, children }: SectionProps) {
  return (
    <section className="section" id={id} aria-labelledby={`${id}-heading`}>
      <div className="section__head">
        <p className="section__eyebrow">{eyebrow}</p>
        <h2 className="section__title" id={`${id}-heading`}>
          {title}
        </h2>
        {description ? <p className="section__description">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}

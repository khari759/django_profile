import { Section } from "./Section";
import type { SkillCategory } from "../types";

interface SkillsProps {
  categories: SkillCategory[];
}

export function Skills({ categories }: SkillsProps) {
  if (categories.length === 0) return null;

  return (
    <Section
      id="skills"
      eyebrow="02 — Skills"
      title="Technologies I work with"
      description="Grouped by where they sit in the stack."
    >
      <div className="skills">
        {categories.map((category) => (
          <article className="card skills__card" key={category.id}>
            <h3 className="skills__category">{category.name}</h3>
            <ul className="chips">
              {category.skills.map((skill) => (
                <li
                  className={`chip chip--${skill.proficiency}`}
                  key={skill.id}
                  title={`${skill.name} — ${skill.proficiency}`}
                >
                  {skill.name}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </Section>
  );
}

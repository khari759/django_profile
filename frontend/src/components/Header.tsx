import { useEffect, useState } from "react";

import type { Theme } from "../hooks/useTheme";

const NAV_ITEMS = [
  { id: "about", label: "About" },
  { id: "skills", label: "Skills" },
  { id: "experience", label: "Experience" },
  { id: "projects", label: "Projects" },
  { id: "contact", label: "Contact" },
];

interface HeaderProps {
  name: string;
  theme: Theme;
  onToggleTheme: () => void;
}

export function Header({ name, theme, onToggleTheme }: HeaderProps) {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<string>("");

  // Highlight the nav link for whichever section is currently in view.
  useEffect(() => {
    const sections = NAV_ITEMS.map((item) => document.getElementById(item.id)).filter(
      (element): element is HTMLElement => element !== null,
    );
    if (sections.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActiveSection(visible.target.id);
      },
      { rootMargin: "-45% 0px -45% 0px", threshold: [0, 0.25, 0.5, 1] },
    );

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("");

  return (
    <header className="header">
      <div className="header__inner">
        <a className="header__brand" href="#top">
          <span className="header__mark" aria-hidden="true">
            {initials || "HK"}
          </span>
          <span className="header__brand-name">{name || "Portfolio"}</span>
        </a>

        <nav
          className={`header__nav ${isMenuOpen ? "header__nav--open" : ""}`}
          aria-label="Sections"
        >
          {NAV_ITEMS.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`header__link ${
                activeSection === item.id ? "header__link--active" : ""
              }`}
              aria-current={activeSection === item.id ? "true" : undefined}
              onClick={() => setMenuOpen(false)}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="header__actions">
          <button
            type="button"
            className="icon-button"
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
          >
            {theme === "dark" ? "☀" : "☾"}
          </button>
          <button
            type="button"
            className="icon-button header__burger"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={isMenuOpen}
            aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          >
            {isMenuOpen ? "✕" : "☰"}
          </button>
        </div>
      </div>
    </header>
  );
}

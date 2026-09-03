import { useEffect, useRef } from "react";

import { mediaUrl } from "../api/client";
import type { Project } from "../types";

interface ProjectDialogProps {
  project: Project;
  onClose: () => void;
}

/** Accessible detail modal: Escape closes it, focus is trapped and restored. */
export function ProjectDialog({ project, onClose }: ProjectDialogProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    closeButtonRef.current?.focus();

    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
        return;
      }
      if (event.key !== "Tab") return;

      const focusable = panelRef.current?.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );
      if (!focusable || focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = overflow;
      previouslyFocused?.focus();
    };
  }, [onClose]);

  const thumbnail = mediaUrl(project.thumbnail);
  const paragraphs = project.description.split(/\n{2,}/).filter(Boolean);

  return (
    <div className="modal">
      {/* Clicking the backdrop closes; it is decorative, the close button is the control. */}
      <div className="modal__backdrop" onClick={onClose} aria-hidden="true" />
      <div
        className="modal__panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="project-dialog-title"
        ref={panelRef}
      >
        <button
          type="button"
          className="modal__close"
          onClick={onClose}
          ref={closeButtonRef}
          aria-label="Close project details"
        >
          ✕
        </button>

        {thumbnail ? (
          <img className="modal__image" src={thumbnail} alt={`${project.title} screenshot`} />
        ) : null}

        <h3 className="modal__title" id="project-dialog-title">
          {project.title}
        </h3>
        {project.role ? <p className="modal__role">Role: {project.role}</p> : null}

        <div className="modal__body">
          {paragraphs.map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>

        {project.technologies.length > 0 ? (
          <ul className="chips">
            {project.technologies.map((tech) => (
              <li className="chip" key={tech.id}>
                {tech.name}
              </li>
            ))}
          </ul>
        ) : null}

        {project.repo_url || project.live_url ? (
          <div className="modal__actions">
            {project.live_url ? (
              <a
                className="button button--primary"
                href={project.live_url}
                target="_blank"
                rel="noreferrer"
              >
                Visit live site
              </a>
            ) : null}
            {project.repo_url ? (
              <a
                className="button button--ghost"
                href={project.repo_url}
                target="_blank"
                rel="noreferrer"
              >
                View source
              </a>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

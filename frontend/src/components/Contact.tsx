import { useState } from "react";

import { Section } from "./Section";
import { ApiValidationError, submitContactMessage } from "../api/client";
import type { ContactPayload, Profile } from "../types";

interface ContactProps {
  profile: Profile;
}

type Status = "idle" | "sending" | "sent" | "error";

const EMPTY_FORM: ContactPayload = { name: "", email: "", subject: "", message: "" };

/** Mirrors the server-side rules so users get feedback without a round trip. */
function validate(form: ContactPayload): Partial<Record<keyof ContactPayload, string>> {
  const errors: Partial<Record<keyof ContactPayload, string>> = {};
  if (form.name.trim().length < 2) errors.name = "Please enter your name.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()))
    errors.email = "Please enter a valid email address.";
  if (form.message.trim().length < 10)
    errors.message = "Please write at least 10 characters.";
  return errors;
}

export function Contact({ profile }: ContactProps) {
  const [form, setForm] = useState<ContactPayload>(EMPTY_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof ContactPayload, string>>>({});
  const [status, setStatus] = useState<Status>("idle");
  const [formMessage, setFormMessage] = useState("");

  function update<K extends keyof ContactPayload>(field: K, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: undefined }));
    if (status === "sent" || status === "error") setStatus("idle");
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const clientErrors = validate(form);
    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      setStatus("error");
      setFormMessage("Please fix the highlighted fields.");
      return;
    }

    setStatus("sending");
    setFormMessage("");
    try {
      await submitContactMessage(form);
      setForm(EMPTY_FORM);
      setErrors({});
      setStatus("sent");
      setFormMessage("Thanks — your message is on its way. I will reply soon.");
    } catch (error) {
      setStatus("error");
      if (error instanceof ApiValidationError) {
        const serverErrors: Partial<Record<keyof ContactPayload, string>> = {};
        for (const [field, messages] of Object.entries(error.fieldErrors)) {
          if (field in EMPTY_FORM && Array.isArray(messages)) {
            serverErrors[field as keyof ContactPayload] = messages[0];
          }
        }
        setErrors(serverErrors);
        setFormMessage(
          error.fieldErrors.detail?.[0] ?? "Please fix the highlighted fields.",
        );
      } else {
        setFormMessage(
          error instanceof Error ? error.message : "Something went wrong. Please try again.",
        );
      }
    }
  }

  const isSending = status === "sending";

  return (
    <Section
      id="contact"
      eyebrow="06 — Contact"
      title="Let's work together"
      description="Send a message and it lands straight in my inbox."
    >
      <div className="contact">
        <div className="contact__aside">
          <p className="contact__lede">
            {profile.is_available_for_work
              ? "I am currently open to full stack roles and interesting freelance work."
              : "I am engaged right now, but always happy to talk."}
          </p>
          <ul className="contact__links">
            <li>
              <span>Email</span>
              <a href={`mailto:${profile.email}`}>{profile.email}</a>
            </li>
            {profile.phone ? (
              <li>
                <span>Phone</span>
                <a href={`tel:${profile.phone.replace(/\s/g, "")}`}>{profile.phone}</a>
              </li>
            ) : null}
            {profile.linkedin_url ? (
              <li>
                <span>LinkedIn</span>
                <a href={profile.linkedin_url} target="_blank" rel="noreferrer">
                  Connect with me
                </a>
              </li>
            ) : null}
            {profile.github_url ? (
              <li>
                <span>GitHub</span>
                <a href={profile.github_url} target="_blank" rel="noreferrer">
                  See my code
                </a>
              </li>
            ) : null}
          </ul>
        </div>

        <form className="card contact__form" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="contact-name">Your name</label>
            <input
              id="contact-name"
              name="name"
              type="text"
              value={form.name}
              onChange={(event) => update("name", event.target.value)}
              aria-invalid={errors.name ? "true" : undefined}
              aria-describedby={errors.name ? "contact-name-error" : undefined}
              disabled={isSending}
              autoComplete="name"
            />
            {errors.name ? (
              <p className="field__error" id="contact-name-error">
                {errors.name}
              </p>
            ) : null}
          </div>

          <div className="field">
            <label htmlFor="contact-email">Email address</label>
            <input
              id="contact-email"
              name="email"
              type="email"
              value={form.email}
              onChange={(event) => update("email", event.target.value)}
              aria-invalid={errors.email ? "true" : undefined}
              aria-describedby={errors.email ? "contact-email-error" : undefined}
              disabled={isSending}
              autoComplete="email"
            />
            {errors.email ? (
              <p className="field__error" id="contact-email-error">
                {errors.email}
              </p>
            ) : null}
          </div>

          <div className="field">
            <label htmlFor="contact-subject">
              Subject <span className="field__optional">(optional)</span>
            </label>
            <input
              id="contact-subject"
              name="subject"
              type="text"
              value={form.subject}
              onChange={(event) => update("subject", event.target.value)}
              disabled={isSending}
            />
          </div>

          <div className="field">
            <label htmlFor="contact-message">Message</label>
            <textarea
              id="contact-message"
              name="message"
              rows={5}
              value={form.message}
              onChange={(event) => update("message", event.target.value)}
              aria-invalid={errors.message ? "true" : undefined}
              aria-describedby={errors.message ? "contact-message-error" : undefined}
              disabled={isSending}
            />
            {errors.message ? (
              <p className="field__error" id="contact-message-error">
                {errors.message}
              </p>
            ) : null}
          </div>

          <button type="submit" className="button button--primary" disabled={isSending}>
            {isSending ? "Sending…" : "Send message"}
          </button>

          {/* role=status so screen readers announce the outcome without stealing focus. */}
          <p
            className={`form-status form-status--${status}`}
            role="status"
            aria-live="polite"
          >
            {formMessage}
          </p>
        </form>
      </div>
    </Section>
  );
}

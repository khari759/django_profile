import type { ContactPayload, FieldErrors, Overview } from "../types";

/**
 * Base URL of the Django API. Configured per environment via `VITE_API_BASE_URL`
 * (see `.env.example`); defaults to the local dev server.
 */
export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

/** A request that reached the server but was rejected — carries DRF's field errors. */
export class ApiValidationError extends Error {
  // Declared as plain fields rather than constructor parameter properties,
  // which `erasableSyntaxOnly` disallows.
  readonly fieldErrors: FieldErrors;

  constructor(fieldErrors: FieldErrors) {
    super("The server rejected the submission.");
    this.name = "ApiValidationError";
    this.fieldErrors = fieldErrors;
  }
}

/** A request that failed for any other reason (network down, 5xx, rate limited). */
export class ApiRequestError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export async function fetchOverview(signal?: AbortSignal): Promise<Overview> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/overview/`, { signal });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiRequestError(
      "Could not reach the portfolio API. Is the Django server running?",
    );
  }

  if (!response.ok) {
    throw new ApiRequestError(
      `The portfolio API responded with ${response.status}.`,
      response.status,
    );
  }
  return (await response.json()) as Overview;
}

export async function submitContactMessage(payload: ContactPayload): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/contact/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiRequestError(
      "Could not reach the server. Please check your connection and try again.",
    );
  }

  if (response.ok) return;

  if (response.status === 400) {
    const body = await readJson(response);
    throw new ApiValidationError((body ?? {}) as FieldErrors);
  }

  if (response.status === 429) {
    throw new ApiRequestError(
      "You have sent several messages already. Please try again a little later.",
      429,
    );
  }

  throw new ApiRequestError(
    "Something went wrong sending your message. Please email me directly instead.",
    response.status,
  );
}

/**
 * Media files come back as paths relative to the API host in some deployments,
 * so resolve them against the API base before use.
 */
export function mediaUrl(path: string | null): string | undefined {
  if (!path) return undefined;
  if (/^https?:\/\//.test(path)) return path;
  return `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}

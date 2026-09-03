import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  ApiRequestError,
  ApiValidationError,
  fetchOverview,
  mediaUrl,
  submitContactMessage,
} from "./client";
import { jsonResponse, overviewFixture } from "../test/fixtures";

const payload = {
  name: "Recruiter",
  email: "recruiter@example.com",
  subject: "Role",
  message: "We would like to talk to you.",
};

describe("fetchOverview", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns the parsed payload", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(overviewFixture)));
    await expect(fetchOverview()).resolves.toEqual(overviewFixture);
  });

  it("requests the overview endpoint", async () => {
    const fetchMock = vi.fn(async (_url: string, _init?: RequestInit) =>
      jsonResponse(overviewFixture),
    );
    vi.stubGlobal("fetch", fetchMock);
    await fetchOverview();
    expect(fetchMock.mock.calls[0]?.[0]).toContain("/api/overview/");
  });

  it("reports an unreachable server with actionable wording", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("Failed to fetch");
      }),
    );
    await expect(fetchOverview()).rejects.toThrow(/Is the Django server running/);
  });

  it("reports a server error status", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse({}, 500)));
    await expect(fetchOverview()).rejects.toMatchObject({ status: 500 });
  });

  it("propagates aborts so React can cancel in-flight loads", async () => {
    const abortError = new DOMException("Aborted", "AbortError");
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw abortError;
      }),
    );
    await expect(fetchOverview()).rejects.toBe(abortError);
  });
});

describe("submitContactMessage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("resolves on 201", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse({ id: 1 }, 201)));
    await expect(submitContactMessage(payload)).resolves.toBeUndefined();
  });

  it("posts JSON to the contact endpoint", async () => {
    const fetchMock = vi.fn(async (_url: string, _init?: RequestInit) =>
      jsonResponse({}, 201),
    );
    vi.stubGlobal("fetch", fetchMock);
    await submitContactMessage(payload);

    const call = fetchMock.mock.calls[0];
    expect(call?.[0]).toContain("/api/contact/");
    expect(call?.[1]?.method).toBe("POST");
    expect(JSON.parse(String(call?.[1]?.body))).toEqual(payload);
  });

  it("surfaces DRF field errors as ApiValidationError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => jsonResponse({ email: ["Enter a valid email address."] }, 400)),
    );
    await expect(submitContactMessage(payload)).rejects.toBeInstanceOf(ApiValidationError);
    await expect(submitContactMessage(payload)).rejects.toMatchObject({
      fieldErrors: { email: ["Enter a valid email address."] },
    });
  });

  it("explains rate limiting in plain language", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse({}, 429)));
    await expect(submitContactMessage(payload)).rejects.toThrow(/try again a little later/);
  });

  it("falls back to a generic message on 500", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse({}, 500)));
    await expect(submitContactMessage(payload)).rejects.toBeInstanceOf(ApiRequestError);
  });

  it("tolerates a 400 with an unparseable body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("<html>nope</html>", { status: 400 })),
    );
    await expect(submitContactMessage(payload)).rejects.toMatchObject({ fieldErrors: {} });
  });
});

describe("mediaUrl", () => {
  it("returns undefined for null", () => {
    expect(mediaUrl(null)).toBeUndefined();
  });

  it("leaves absolute URLs untouched", () => {
    expect(mediaUrl("https://cdn.example.com/a.png")).toBe("https://cdn.example.com/a.png");
  });

  it("resolves a relative path against the API base", () => {
    expect(mediaUrl("/media/resume/cv.pdf")).toMatch(/\/media\/resume\/cv\.pdf$/);
    expect(mediaUrl("/media/resume/cv.pdf")).toMatch(/^https?:\/\//);
  });

  it("inserts the missing slash on a bare path", () => {
    expect(mediaUrl("media/a.png")).toMatch(/\/media\/a\.png$/);
  });
});

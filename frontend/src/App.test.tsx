import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { jsonResponse, overviewFixture } from "./test/fixtures";

/** Routes overview GETs to `overview` and contact POSTs to `contact`. */
function stubApi({
  overview = () => jsonResponse(overviewFixture),
  contact = () => jsonResponse({ id: 1 }, 201),
}: {
  overview?: () => Response;
  contact?: () => Response;
} = {}) {
  const fetchMock = vi.fn(async (url: string | URL, init?: RequestInit) => {
    const href = url.toString();
    if (href.includes("/api/contact/") && init?.method === "POST") return contact();
    if (href.includes("/api/overview/")) return overview();
    throw new Error(`Unexpected request: ${init?.method ?? "GET"} ${href}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("shows a loading state before the API responds", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => {})));
    render(<App />);
    expect(screen.getByText(/loading portfolio/i)).toBeInTheDocument();
  });

  it("renders the profile once loaded", async () => {
    stubApi();
    render(<App />);
    expect(
      await screen.findByRole("heading", { name: "Hari Krishna Komire", level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByText("Full Stack Software Engineer")).toBeInTheDocument();

    // The availability wording also appears in the About card, so scope to the hero.
    const hero = screen.getByRole("region", { name: "Introduction" });
    expect(within(hero).getByText(/open to new opportunities/i)).toBeInTheDocument();
    expect(within(hero).getByRole("link", { name: /download cv/i })).toHaveAttribute(
      "href",
      expect.stringContaining("/media/resume/cv.pdf"),
    );
  });

  it("renders every content section", async () => {
    stubApi();
    render(<App />);
    await screen.findByRole("heading", { name: "Hari Krishna Komire", level: 1 });

    for (const heading of [
      "A bit about me",
      "Technologies I work with",
      "Where I have worked",
      "Things I have built",
      "Education & certifications",
      "Let's work together",
    ]) {
      expect(screen.getByRole("heading", { name: heading, level: 2 })).toBeInTheDocument();
    }
  });

  it("splits the summary into paragraphs", async () => {
    stubApi();
    render(<App />);
    expect(await screen.findByText("First paragraph about me.")).toBeInTheDocument();
    expect(screen.getByText("Second paragraph about me.")).toBeInTheDocument();
  });

  it("shows experience highlights and a computed duration", async () => {
    stubApi();
    render(<App />);
    expect(
      await screen.findByText("Built RESTful APIs with Django REST Framework."),
    ).toBeInTheDocument();
    expect(screen.getByText(/Mar 2023 — Present/)).toBeInTheDocument();
    expect(screen.getByText("Current")).toBeInTheDocument();
  });

  it("renders an error state with a working retry", async () => {
    const failing = vi.fn(async () => {
      throw new TypeError("Failed to fetch");
    });
    vi.stubGlobal("fetch", failing);
    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/portfolio unavailable/i);

    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(overviewFixture)));
    await userEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(
      await screen.findByRole("heading", { name: "Hari Krishna Komire", level: 1 }),
    ).toBeInTheDocument();
  });

  it("explains an empty database instead of rendering a blank page", async () => {
    stubApi({
      overview: () =>
        jsonResponse({
          profile: null,
          skill_categories: [],
          experience: [],
          projects: [],
          education: [],
          certifications: [],
        }),
    });
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/no content yet/i);
    expect(screen.getByText(/seed_portfolio/)).toBeInTheDocument();
  });
});

describe("Projects", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("lists all projects by default", async () => {
    stubApi();
    render(<App />);
    expect(
      await screen.findByRole("heading", { name: "AbsoluteCORE Payroll", level: 3 }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Portfolio Site", level: 3 })).toBeInTheDocument();
  });

  it("filters projects by technology", async () => {
    stubApi();
    render(<App />);
    await screen.findByRole("heading", { name: "AbsoluteCORE Payroll", level: 3 });

    await userEvent.click(screen.getByRole("button", { name: /^React\.js/ }));

    expect(screen.getByRole("heading", { name: "Portfolio Site", level: 3 })).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "AbsoluteCORE Payroll", level: 3 }),
    ).not.toBeInTheDocument();
  });

  it("restores the full list via the All filter", async () => {
    stubApi();
    render(<App />);
    await screen.findByRole("heading", { name: "AbsoluteCORE Payroll", level: 3 });

    await userEvent.click(screen.getByRole("button", { name: /^React\.js/ }));
    await userEvent.click(screen.getByRole("button", { name: /^All/ }));

    expect(
      screen.getByRole("heading", { name: "AbsoluteCORE Payroll", level: 3 }),
    ).toBeInTheDocument();
  });

  it("opens a project dialog and closes it with Escape", async () => {
    stubApi();
    render(<App />);
    await screen.findByRole("heading", { name: "AbsoluteCORE Payroll", level: 3 });

    const cards = screen.getAllByRole("button", { name: /read more/i });
    await userEvent.click(cards[0]);

    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText("Payroll intro paragraph.")).toBeInTheDocument();
    expect(within(dialog).getByText("Payroll detail paragraph.")).toBeInTheDocument();
    expect(within(dialog).getByRole("link", { name: /view source/i })).toHaveAttribute(
      "href",
      "https://github.com/example/payroll",
    );

    await userEvent.keyboard("{Escape}");
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("closes the dialog with the close button", async () => {
    stubApi();
    render(<App />);
    await screen.findByRole("heading", { name: "AbsoluteCORE Payroll", level: 3 });

    await userEvent.click(screen.getAllByRole("button", { name: /read more/i })[0]);
    await screen.findByRole("dialog");
    await userEvent.click(screen.getByRole("button", { name: /close project details/i }));

    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });
});

describe("Contact form", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  async function loadApp(options?: Parameters<typeof stubApi>[0]) {
    const fetchMock = stubApi(options);
    render(<App />);
    await screen.findByRole("heading", { name: "Hari Krishna Komire", level: 1 });
    return fetchMock;
  }

  it("rejects empty input client-side without calling the API", async () => {
    const fetchMock = await loadApp();
    const callsBefore = fetchMock.mock.calls.length;

    await userEvent.click(screen.getByRole("button", { name: /send message/i }));

    expect(await screen.findByText("Please enter your name.")).toBeInTheDocument();
    expect(screen.getByText("Please enter a valid email address.")).toBeInTheDocument();
    expect(screen.getByText("Please write at least 10 characters.")).toBeInTheDocument();
    expect(fetchMock.mock.calls.length).toBe(callsBefore);
  });

  it("submits valid input and confirms success", async () => {
    const fetchMock = await loadApp();

    await userEvent.type(screen.getByLabelText(/your name/i), "Recruiter");
    await userEvent.type(screen.getByLabelText(/email address/i), "recruiter@example.com");
    await userEvent.type(screen.getByLabelText(/^message$/i), "We have a role for you.");
    await userEvent.click(screen.getByRole("button", { name: /send message/i }));

    expect(await screen.findByText(/your message is on its way/i)).toBeInTheDocument();

    const contactCall = fetchMock.mock.calls.find(([url]) =>
      url.toString().includes("/api/contact/"),
    );
    expect(contactCall).toBeDefined();
    expect(JSON.parse((contactCall?.[1]?.body as string) ?? "{}")).toEqual({
      name: "Recruiter",
      email: "recruiter@example.com",
      subject: "",
      message: "We have a role for you.",
    });
  });

  it("clears the form after a successful send", async () => {
    await loadApp();

    await userEvent.type(screen.getByLabelText(/your name/i), "Recruiter");
    await userEvent.type(screen.getByLabelText(/email address/i), "recruiter@example.com");
    await userEvent.type(screen.getByLabelText(/^message$/i), "We have a role for you.");
    await userEvent.click(screen.getByRole("button", { name: /send message/i }));

    await screen.findByText(/your message is on its way/i);
    expect(screen.getByLabelText(/your name/i)).toHaveValue("");
    expect(screen.getByLabelText(/^message$/i)).toHaveValue("");
  });

  it("shows server-side field errors", async () => {
    await loadApp({
      contact: () => jsonResponse({ email: ["Enter a valid email address."] }, 400),
    });

    await userEvent.type(screen.getByLabelText(/your name/i), "Recruiter");
    await userEvent.type(screen.getByLabelText(/email address/i), "recruiter@example.com");
    await userEvent.type(screen.getByLabelText(/^message$/i), "We have a role for you.");
    await userEvent.click(screen.getByRole("button", { name: /send message/i }));

    expect(await screen.findByText("Enter a valid email address.")).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toHaveAttribute("aria-invalid", "true");
  });

  it("explains rate limiting", async () => {
    await loadApp({ contact: () => jsonResponse({}, 429) });

    await userEvent.type(screen.getByLabelText(/your name/i), "Recruiter");
    await userEvent.type(screen.getByLabelText(/email address/i), "recruiter@example.com");
    await userEvent.type(screen.getByLabelText(/^message$/i), "We have a role for you.");
    await userEvent.click(screen.getByRole("button", { name: /send message/i }));

    expect(await screen.findByText(/try again a little later/i)).toBeInTheDocument();
  });
});

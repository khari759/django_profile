import { afterEach, describe, expect, it, vi } from "vitest";

import { formatDateRange, formatDuration, formatMonthYear } from "./dates";

describe("formatMonthYear", () => {
  it("formats an ISO date as month and year", () => {
    expect(formatMonthYear("2023-03-01")).toBe("Mar 2023");
  });

  it("returns an empty string for null", () => {
    expect(formatMonthYear(null)).toBe("");
  });

  it("returns an empty string for unparseable input", () => {
    expect(formatMonthYear("not-a-date")).toBe("");
  });
});

describe("formatDateRange", () => {
  it("renders a closed range", () => {
    expect(formatDateRange("2022-09-01", "2023-03-01")).toBe("Sep 2022 — Mar 2023");
  });

  it("renders an open range as Present", () => {
    expect(formatDateRange("2023-03-01", null)).toBe("Mar 2023 — Present");
  });
});

describe("formatDuration", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("counts whole years", () => {
    expect(formatDuration("2022-01-01", "2022-12-01")).toBe("1 yr");
  });

  it("counts years and months", () => {
    expect(formatDuration("2022-01-01", "2023-06-01")).toBe("1 yr 6 mos");
  });

  it("uses singular units for one month", () => {
    expect(formatDuration("2023-03-01", "2023-03-01")).toBe("1 mo");
  });

  it("measures an open range up to today", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2024-03-15T00:00:00Z"));
    expect(formatDuration("2023-03-01", null)).toBe("1 yr 1 mo");
  });

  it("returns an empty string when the end precedes the start", () => {
    expect(formatDuration("2024-01-01", "2023-01-01")).toBe("");
  });

  it("returns an empty string for invalid input", () => {
    expect(formatDuration("nonsense", null)).toBe("");
  });
});

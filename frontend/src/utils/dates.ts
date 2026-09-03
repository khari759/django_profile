/** Date helpers for the experience timeline. */

// en-US is pinned deliberately: it abbreviates every month to three letters
// ("Sep"), whereas en-GB yields "Sept" and reads inconsistently in a timeline.
const MONTH_YEAR = new Intl.DateTimeFormat("en-US", {
  month: "short",
  year: "numeric",
});

/** "2023-03-01" -> "Mar 2023". Returns "" for null/unparseable input. */
export function formatMonthYear(isoDate: string | null): string {
  if (!isoDate) return "";
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) return "";
  return MONTH_YEAR.format(date);
}

/** "Mar 2023 — Present" or "Sep 2022 — Mar 2023". */
export function formatDateRange(start: string, end: string | null): string {
  const from = formatMonthYear(start);
  const to = end ? formatMonthYear(end) : "Present";
  return from ? `${from} — ${to}` : to;
}

/**
 * Whole months between two dates, rendered as "1 yr 6 mos".
 * `end` of null means "up to today".
 */
export function formatDuration(start: string, end: string | null): string {
  const from = new Date(start);
  const to = end ? new Date(end) : new Date();
  if (Number.isNaN(from.getTime()) || Number.isNaN(to.getTime())) return "";

  let months =
    (to.getFullYear() - from.getFullYear()) * 12 + (to.getMonth() - from.getMonth());
  if (months < 0) return "";
  months += 1; // Count the starting month itself, as CVs conventionally do.

  const years = Math.floor(months / 12);
  const remainder = months % 12;
  const parts: string[] = [];
  if (years > 0) parts.push(`${years} yr${years === 1 ? "" : "s"}`);
  if (remainder > 0) parts.push(`${remainder} mo${remainder === 1 ? "" : "s"}`);
  return parts.join(" ") || "1 mo";
}

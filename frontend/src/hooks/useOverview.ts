import { useCallback, useEffect, useState } from "react";

import { fetchOverview } from "../api/client";
import type { Overview } from "../types";

type State =
  | { status: "loading" }
  | { status: "ready"; data: Overview }
  | { status: "error"; message: string };

/** Loads the whole page payload, with a `retry` for the error state. */
export function useOverview() {
  const [state, setState] = useState<State>({ status: "loading" });
  // Bumping this re-runs the effect; the loading state is set by `retry`
  // itself rather than inside the effect, which would cascade a render.
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    fetchOverview(controller.signal)
      .then((data) => setState({ status: "ready", data }))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        setState({
          status: "error",
          message:
            error instanceof Error ? error.message : "The portfolio failed to load.",
        });
      });

    return () => controller.abort();
  }, [attempt]);

  const retry = useCallback(() => {
    setState({ status: "loading" });
    setAttempt((value) => value + 1);
  }, []);

  return { state, retry };
}

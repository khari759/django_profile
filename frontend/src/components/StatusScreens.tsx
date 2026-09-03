import { API_BASE_URL } from "../api/client";

export function LoadingScreen() {
  return (
    <div className="status-screen" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <p>Loading portfolio…</p>
    </div>
  );
}

interface ErrorScreenProps {
  message: string;
  onRetry: () => void;
}

export function ErrorScreen({ message, onRetry }: ErrorScreenProps) {
  return (
    <div className="status-screen status-screen--error" role="alert">
      <h1>Portfolio unavailable</h1>
      <p>{message}</p>
      <p className="status-screen__hint">
        Expecting the API at <code>{API_BASE_URL}</code>. Start the backend with{" "}
        <code>python manage.py runserver</code>, or set <code>VITE_API_BASE_URL</code>.
      </p>
      <button type="button" className="button button--primary" onClick={onRetry}>
        Try again
      </button>
    </div>
  );
}

export function EmptyProfileScreen() {
  return (
    <div className="status-screen" role="alert">
      <h1>No content yet</h1>
      <p>
        The API is reachable but has no profile. Seed it with{" "}
        <code>python manage.py seed_portfolio</code>, then reload.
      </p>
    </div>
  );
}

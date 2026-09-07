# Developer Portfolio — Django REST Framework + React

A content-managed portfolio site. Every section the visitor sees — profile, skills,
experience, projects, education, certifications — is a Django model editable from the
admin, so updating the site never means editing code or redeploying.

**Live site:** <https://khari759.github.io/django_profile/>
**API:** <https://portfolio-api-f06z.onrender.com> · **Admin:** `/admin/`

> The API runs on Render's free tier and sleeps after ~15 minutes idle, so the first
> request can take 30–50 seconds to wake it.

**Setting this up or operating it?** [SETUP.md](SETUP.md) has the full environment
variable reference, deployment steps, verification commands and troubleshooting.

**Backend:** Python 3.13 · Django 6.1 · Django REST Framework · PostgreSQL / SQLite
**Frontend:** React 19 · TypeScript · Vite · plain CSS (no UI framework)
**Tooling:** pytest · Vitest · Testing Library · ruff · oxlint · Docker · GitHub Actions

---

## Table of contents

- [What it does](#what-it-does)
- [Architecture](#architecture)
- [Quick start](#quick-start)
- [API reference](#api-reference)
- [Editing your content](#editing-your-content)
- [Tests and linting](#tests-and-linting)
- [Docker](#docker)
- [Deploying for free](#deploying-for-free)
- [Project layout](#project-layout)

---

## What it does

- **Admin-managed content.** Add a project or a job in `/admin/` and it appears on the
  site immediately. No hardcoded content in the React app.
- **One-request page load.** `GET /api/overview/` returns every section in a single
  payload, so the page renders after one round trip rather than seven.
- **Working contact form.** Submissions are validated on both sides, stored in the
  database, emailed to you, and rate limited to 5 per hour per IP.
- **Project filtering.** Filter chips are derived from the technologies actually
  attached to your projects, so they stay correct as you add work.
- **Light and dark themes.** Follows the OS preference, remembers an explicit choice,
  and applies it before first paint so there is no flash of the wrong palette.
- **Accessible by default.** Skip link, labelled landmarks, keyboard-navigable modal
  with focus trapping and restore, `aria-invalid` wired to error messages,
  `prefers-reduced-motion` respected.
- **Graceful failure.** If the API is down the site explains what to start rather than
  rendering a blank page.

## Architecture

```text
┌──────────────────────────┐         ┌────────────────────────────────┐
│  React 19 + TypeScript   │         │      Django 6.1 + DRF          │
│  (Vite, static hosting)  │         │      (gunicorn)                │
│                          │         │                                │
│  useOverview() ──────────┼── GET ──┼─▶ /api/overview/               │
│                          │         │   aggregates every section     │
│  Contact form ───────────┼── POST ─┼─▶ /api/contact/  (throttled)   │
│                          │         │        │                       │
└──────────────────────────┘         │        ├─▶ ContactMessage row  │
                                     │        └─▶ notification email  │
                                     │                                │
                                     │   /admin/  ── content CMS      │
                                     └───────────────┬────────────────┘
                                                     │
                                            PostgreSQL / SQLite
```

The frontend holds no content of its own — it is a rendering layer over the API. That
is the point: the same build serves any content the admin contains.

## Quick start

Requires Python 3.11+ and Node 20+.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env               # defaults work as-is for local dev

python manage.py migrate
python manage.py seed_portfolio    # loads the content in seed_portfolio.py
python manage.py createsuperuser   # for /admin/
python manage.py runserver         # http://127.0.0.1:8000
```

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

The site is at **http://localhost:5173**, the admin at
**http://127.0.0.1:8000/admin/**.

SQLite is the default so nothing else needs installing. To use PostgreSQL instead, set
`DATABASE_URL` in `backend/.env` — no code changes needed:

```bash
DATABASE_URL=postgres://portfolio:portfolio@localhost:5432/portfolio
```

## API reference

Base URL `http://127.0.0.1:8000`. All read endpoints are public and unpaginated.

| Method | Endpoint                   | Purpose                                        |
| ------ | -------------------------- | ---------------------------------------------- |
| `GET`  | `/api/overview/`           | Every section in one payload (used by the app) |
| `GET`  | `/api/profile/`            | Name, headline, summary, links, CV             |
| `GET`  | `/api/skills/`             | Skills nested under their categories           |
| `GET`  | `/api/experience/`         | Roles with achievement bullets                 |
| `GET`  | `/api/projects/`           | Published projects                             |
| `GET`  | `/api/projects/{slug}/`    | A single project                               |
| `GET`  | `/api/education/`          | Degrees                                        |
| `GET`  | `/api/certifications/`     | Certifications                                 |
| `POST` | `/api/contact/`            | Submit a message (5/hour per IP)               |
| `GET`  | `/api/health/`             | Liveness probe                                 |

Project list filters:

```bash
curl "http://127.0.0.1:8000/api/projects/?featured=true"   # featured only
curl "http://127.0.0.1:8000/api/projects/?tech=django"     # by technology slug
```

Contact submission:

```bash
curl -X POST http://127.0.0.1:8000/api/contact/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Recruiter","email":"r@example.com","message":"Let us talk."}'
```

Validation failures return `400` with DRF's field-error shape, which the form maps back
onto the offending inputs:

```json
{ "email": ["Enter a valid email address."] }
```

## Editing your content

Two ways, and they are equivalent:

**Through the admin** (best for day-to-day updates) — go to `/admin/`, and edit
Profile, Skills, Experience, Projects, Education or Certifications. Skills and
experience bullets are edited inline under their parents. Uploaded avatars, CVs and
project screenshots land in `backend/media/`.

**Through the seed command** (best for version-controlled content) — edit the data at
the top of `backend/portfolio/management/commands/seed_portfolio.py`, then:

```bash
python manage.py seed_portfolio            # upsert, keeps admin edits elsewhere
python manage.py seed_portfolio --reset    # wipe content and reseed from the file
```

Both are safe to re-run: the command upserts rather than duplicating.

Notes on specific fields:

- **Profile is a singleton.** The admin hides "Add" once one exists.
- **Projects have `is_published`.** Uncheck it to draft a project without deleting it —
  the API hides unpublished projects entirely.
- **`is_featured`** adds the Featured badge and powers `?featured=true`.
- **`display_order`** controls ordering everywhere; lower comes first.
- **Contact messages are read-only** in the admin, with a "mark as read" action.

## Tests and linting

```bash
# Backend (from backend/, venv active)
pytest                      # 51 tests
ruff check .                # lint
ruff format .               # format
python manage.py check --deploy   # production-readiness audit

# Frontend (from frontend/)
npm run test                # 49 tests
npm run test:coverage       # with coverage report
npm run typecheck           # tsc, strict mode
npm run lint                # oxlint
npm run build               # production build
```

Backend coverage spans model validation and slug collisions, every API endpoint,
throttling, the mail-failure path, and the seed command's idempotency. Frontend
coverage spans the API client's error branches, date formatting, and the rendered app —
loading, error and empty states, project filtering, the modal's keyboard behaviour, and
the contact form's client- and server-side validation.

CI runs all of it on every push and pull request, plus a missing-migrations check and
both Docker builds.

## Docker

```bash
docker compose up --build
```

Brings up PostgreSQL, the API (migrated and seeded automatically) and the
nginx-served frontend:

- Site — http://localhost:5173
- API — http://localhost:8000
- Admin — http://localhost:8000/admin/ (create a user with
  `docker compose exec backend python manage.py createsuperuser`)

## Deploying for free

The two halves deploy independently: static frontend on GitHub Pages, API on Render.

### Frontend — GitHub Pages

Already wired up in [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml).

1. In the repository, go to **Settings → Pages** and set **Source** to
   **GitHub Actions**.
2. Push to `main`. The workflow builds and publishes automatically.
3. The site goes live at `https://<username>.github.io/<repo>/`.

The workflow sets Vite's `base` to the repository name so asset paths resolve, and
copies `index.html` to `404.html` so deep links work without server rewrites.

### Backend — Render free tier

[`render.yaml`](render.yaml) is a Blueprint, so Render provisions everything from it.

1. Sign in at [render.com](https://render.com) → **New → Blueprint** → connect this
   repository.
2. Render creates the web service and a free PostgreSQL database, generates
   `DJANGO_SECRET_KEY`, and runs migrations plus the seed on boot.
3. Copy the service URL, e.g. `https://portfolio-api.onrender.com`.

### Connect the two

1. In the repository: **Settings → Secrets and variables → Actions → Variables →
   New repository variable**, named `VITE_API_BASE_URL`, set to your Render URL.
2. Re-run the Pages workflow (**Actions → Deploy frontend to GitHub Pages → Run
   workflow**) so the new API URL is baked into the build.
3. In Render, confirm `DJANGO_CORS_ALLOWED_ORIGINS` and
   `DJANGO_CSRF_TRUSTED_ORIGINS` contain your Pages origin
   (`https://<username>.github.io`).

### The admin account

Set three environment variables in the Render dashboard (**your service → Environment**):

| Variable                    | Value                             |
| --------------------------- | --------------------------------- |
| `DJANGO_SUPERUSER_USERNAME` | your admin username               |
| `DJANGO_SUPERUSER_EMAIL`    | your email                        |
| `DJANGO_SUPERUSER_PASSWORD` | a long random password            |

`ensure_superuser` runs on every boot and creates or updates that account. This is
deliberate rather than a one-off `createsuperuser`: the free database is dropped after
30 days, and a hand-made account would vanish with it. Rotating the password is just a
matter of changing the variable and redeploying.

Locally, create the user interactively instead — with the variables unset the command
does nothing:

```bash
python manage.py createsuperuser
```

**Free-tier limitations to expect:**

- The Render service sleeps after ~15 minutes idle. The first request after that takes
  roughly 30–50 seconds, so a cold visit shows the loading state for a while.
- Free PostgreSQL expires after 30 days and has to be recreated. Content is reseeded on
  boot from `seed_portfolio.py`, which is why keeping your content there is worthwhile.
- The filesystem is ephemeral: uploaded avatars, CVs and screenshots are lost on
  redeploy. Commit them to the repo or attach S3/Cloudinary if you need them to persist.

## Project layout

```text
.
├── backend/
│   ├── config/                     # settings, root URLs, WSGI
│   │   └── settings.py             # env-driven; SQLite -> PostgreSQL via DATABASE_URL
│   ├── portfolio/
│   │   ├── models.py               # Profile, Skill, Experience, Project, ...
│   │   ├── serializers.py          # JSON contract
│   │   ├── views.py                # read-only API + throttled contact endpoint
│   │   ├── urls.py
│   │   ├── admin.py                # the CMS: inlines, singleton guard, bulk actions
│   │   ├── management/commands/
│   │   │   └── seed_portfolio.py   # version-controlled content, idempotent
│   │   └── tests/                  # pytest suites
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.ts           # typed fetch layer with error classes
│   │   ├── components/             # Hero, Skills, Timeline, Projects, Contact, ...
│   │   ├── hooks/                  # useOverview, useTheme
│   │   ├── utils/dates.ts          # duration and range formatting
│   │   ├── types.ts                # mirrors the serializers
│   │   └── index.css               # design tokens + all styles
│   ├── Dockerfile                  # multi-stage build -> nginx
│   ├── nginx.conf                  # SPA fallback + asset caching
│   └── .env.example
├── .github/workflows/
│   ├── ci.yml                      # lint, typecheck, tests, Docker builds
│   └── deploy-pages.yml            # frontend -> GitHub Pages
├── docker-compose.yml              # full stack with PostgreSQL
└── render.yaml                     # API -> Render free tier
```

## License

MIT — see [LICENSE](LICENSE).

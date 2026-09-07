# Setup & Deployment Guide

End-to-end instructions for running this portfolio locally and deploying it for free,
plus the failure modes that actually came up while deploying it the first time.

The [README](README.md) covers what the project is and how the code is organised. This
document covers operating it.

**Live:** <https://khari759.github.io/django_profile/>
**API:** <https://portfolio-api-f06z.onrender.com>
**Admin:** <https://portfolio-api-f06z.onrender.com/admin/>

---

## Contents

- [How the pieces fit](#how-the-pieces-fit)
- [Running it locally](#running-it-locally)
- [Environment variables](#environment-variables)
- [Deploying the frontend (GitHub Pages)](#deploying-the-frontend-github-pages)
- [Deploying the backend (Render)](#deploying-the-backend-render)
- [The admin account](#the-admin-account)
- [Contact form email](#contact-form-email)
- [Custom domain](#custom-domain)
- [Verifying a deployment](#verifying-a-deployment)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## How the pieces fit

Two independently deployed halves that only meet over HTTP:

```text
GitHub push to main
        │
        ├─▶ .github/workflows/ci.yml ......... lint, typecheck, tests, Docker builds
        │
        └─▶ .github/workflows/deploy-pages.yml
                 │  npm ci && npm run build
                 │  VITE_BASE_PATH  = /<repo>/ (or / for a user site or custom domain)
                 │  VITE_API_BASE_URL from frontend/.env.production
                 ▼
            GitHub Pages ── static files, free, no cold start
                 │
                 │  fetch()
                 ▼
            Render web service ── Django + gunicorn
                 │  start command: migrate → seed_portfolio → gunicorn
                 ▼
            PostgreSQL (free tier)
```

The API URL is **baked into the JavaScript at build time**, not read at runtime. Changing
which API the site talks to therefore requires a rebuild, not just a restart.

Render deploys are triggered separately from Pages deploys — a push does not
automatically update both unless Auto-Deploy is enabled on Render.

---

## Running it locally

Requires **Python 3.11+** and **Node 20+**. Nothing else — SQLite is the default database.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env               # defaults are fine for local work

python manage.py migrate
python manage.py seed_portfolio    # loads content from seed_portfolio.py
python manage.py createsuperuser   # your local admin login
python manage.py runserver         # http://127.0.0.1:8000
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

Open <http://localhost:5173>. The admin is at <http://127.0.0.1:8000/admin/>.

Both must be running: the frontend has no content of its own and will show
"Portfolio unavailable" if the API is not reachable.

### Using PostgreSQL locally

Set `DATABASE_URL` in `backend/.env`. No code changes are needed:

```bash
DATABASE_URL=postgres://portfolio:portfolio@localhost:5432/portfolio
```

Or run the whole stack in containers:

```bash
docker compose up --build          # site :5173, API :8000, PostgreSQL :5432
```

---

## Environment variables

All backend configuration is environment-driven. Only `DATABASE_URL` and
`DJANGO_SECRET_KEY` matter in production; everything else has a working default.

### Core

| Variable | Default | Notes |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | insecure dev key | **Must** be set in production. Render generates one. |
| `DJANGO_DEBUG` | `True` | Set `False` in production. Also switches email to SMTP. |
| `DATABASE_URL` | local SQLite file | Any URL `dj-database-url` understands. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | Comma-separated. A leading dot is a wildcard: `.onrender.com`. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Must contain the exact frontend origin, scheme included. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | empty | Needed for admin logins over HTTPS. |
| `DJANGO_TIME_ZONE` | `Asia/Kolkata` | Affects dates rendered on the site. |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` when `DEBUG=False` | Set `False` on hosts that already redirect to HTTPS, such as Render. |

### Admin bootstrap

Applied on every boot by `ensure_superuser`, which `seed_portfolio` calls. Leave unset
to disable entirely — that is what makes local runs unaffected.

| Variable | Notes |
| --- | --- |
| `DJANGO_SUPERUSER_USERNAME` | Required to create anything. |
| `DJANGO_SUPERUSER_PASSWORD` | Required. Re-applied on every boot, so editing it rotates the password. |
| `DJANGO_SUPERUSER_EMAIL` | Optional. |

### Email

| Variable | Default | Notes |
| --- | --- | --- |
| `CONTACT_NOTIFY_EMAIL` | empty | Where notifications go. **Empty means no email is attempted at all.** |
| `DJANGO_EMAIL_BACKEND` | console in debug, SMTP otherwise | Rarely needs setting. |
| `DJANGO_EMAIL_HOST` | `localhost` | e.g. `smtp.gmail.com`. |
| `DJANGO_EMAIL_PORT` | `587` (`465` with SSL) | |
| `DJANGO_EMAIL_USER` | empty | Full email address. |
| `DJANGO_EMAIL_PASSWORD` | empty | For Gmail this must be an **App Password**. |
| `DJANGO_EMAIL_USE_TLS` | `True` | |
| `DJANGO_EMAIL_USE_SSL` | `False` | Enabling it forces TLS off — the backend rejects both. |
| `DJANGO_EMAIL_TIMEOUT` | `10` | Seconds. |
| `DJANGO_DEFAULT_FROM_EMAIL` | `DJANGO_EMAIL_USER`, else `portfolio@localhost` | Gmail rewrites this to the authenticated account. |

### Frontend

Build-time only, and **inlined into the public bundle** — never put a secret here.

| Variable | Set in | Notes |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `frontend/.env.production` (tracked) | The deployed API URL. |
| `VITE_BASE_PATH` | the Pages workflow | Computed; do not set by hand. |

To repoint the site without a commit, set a `VITE_API_BASE_URL` **repository variable**
(Settings → Secrets and variables → Actions → Variables). The workflow writes it to
`.env.production.local`, which Vite ranks above the committed file.

---

## Deploying the frontend (GitHub Pages)

Already configured in [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml).
It runs on every push to `main` and needs no setup — `configure-pages` is passed
`enablement: true`, so it switches the repository to Actions-based Pages itself.

The site publishes to `https://<user>.github.io/<repo>/`.

Two details the workflow handles that are easy to get wrong by hand:

- **Base path.** A project site is served from `/<repo>/`, but a user site
  (`<user>.github.io`) and any custom domain are served from `/`. The workflow computes
  this. Hardcoding it makes every asset 404 after a rename.
- **Deep links.** Pages has no rewrite rules, so `index.html` is copied to `404.html`.

To deploy manually: **Actions → Deploy frontend to GitHub Pages → Run workflow**.

---

## Deploying the backend (Render)

[`render.yaml`](render.yaml) is a Blueprint — Render provisions the web service and
database from it.

1. [render.com](https://render.com) → **New → Blueprint** → select this repository.
2. Fill in the prompted variables (those marked `sync: false` are never stored in git):
   `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`,
   `CONTACT_NOTIFY_EMAIL`, `DJANGO_EMAIL_USER`, `DJANGO_EMAIL_PASSWORD`.
3. **Apply.** First build takes 3–5 minutes.
4. Copy the service URL, then either put it in `frontend/.env.production` and push, or
   set the `VITE_API_BASE_URL` repository variable and re-run the Pages workflow.

On every boot the start command runs:

```text
migrate --noinput  →  seed_portfolio  →  ensure_superuser  →  gunicorn
```

so a freshly created database comes back fully populated, admin account included.

### Turn on Auto-Deploy

**Settings → Build & Deploy → Auto-Deploy → Yes.**

Without this, pushing to GitHub updates Pages but **not** Render, and the two halves
drift apart silently. This caused several confusing rounds during the first deploy.

### Changing `render.yaml` after the service exists

Render applies `render.yaml` edits only when the **Blueprint is synced**, which is a
separate action from deploying code. A plain deploy picks up new code but keeps the old
start command.

Because of that, anything that must run on boot is invoked from `seed_portfolio`, which
the existing start command already calls. That keeps a plain code deploy sufficient.

---

## The admin account

Set the three `DJANGO_SUPERUSER_*` variables and redeploy. `ensure_superuser` creates
the account when missing and re-applies the password when present.

This runs on every boot rather than once, deliberately: the free PostgreSQL instance is
dropped after 30 days, and a hand-made account would disappear with it.

Locally, use `python manage.py createsuperuser` instead — with the variables unset the
bootstrap does nothing.

> Render's **Shell** is a paid feature, so on the free tier there is no way to run a
> one-off `createsuperuser` against production. The environment-variable path is the
> only option, which is why it exists.

---

## Contact form email

Submissions are always stored in the database and visible under **admin → Contact
messages**. Email is an optional notification on top; if sending fails the message is
still kept, and the error is logged rather than surfaced to the visitor.

**No email is attempted unless `CONTACT_NOTIFY_EMAIL` is set.**

### Gmail

Gmail rejects normal account passwords for SMTP. Create an App Password:

1. Enable [2-Step Verification](https://myaccount.google.com/signinoptions/two-step-verification).
2. Go to [App Passwords](https://myaccount.google.com/apppasswords), create one, and
   copy the 16-character code.
3. Set on Render:

   | Variable | Value |
   | --- | --- |
   | `CONTACT_NOTIFY_EMAIL` | your address |
   | `DJANGO_EMAIL_USER` | your Gmail address |
   | `DJANGO_EMAIL_PASSWORD` | the 16-character App Password |
   | `DJANGO_EMAIL_HOST` | `smtp.gmail.com` |
   | `DJANGO_EMAIL_PORT` | `587` |
   | `DJANGO_EMAIL_USE_TLS` | `True` |

4. Redeploy, then submit through the live form.

Gmail's SMTP allows roughly 500 messages a day — far beyond what a contact form needs.
The endpoint is separately rate limited to 5 submissions per hour per IP.

---

## Custom domain

Hosting stays free; only the domain costs money. Buy at Cloudflare Registrar (at-cost)
or Namecheap — roughly ₹200/yr for `.xyz`, ₹900 for `.com`, ₹1,100 for `.dev`.

1. Set a `CUSTOM_DOMAIN` repository variable to the bare domain. The workflow writes the
   `CNAME` file and switches the base path to `/`.
2. At the registrar, point DNS at GitHub Pages:

   ```text
   A      @     185.199.108.153
   A      @     185.199.109.153
   A      @     185.199.110.153
   A      @     185.199.111.153
   CNAME  www   <user>.github.io
   ```

3. Add the domain under **Settings → Pages → Custom domain**, then enable
   **Enforce HTTPS** once the certificate is issued (can take up to an hour).
4. Add the new origin to `DJANGO_CORS_ALLOWED_ORIGINS` and
   `DJANGO_CSRF_TRUSTED_ORIGINS` on Render, or the site will load but every API call
   will be blocked by the browser.

A **free** alternative to the root URL: rename the repository to `<user>.github.io`.
The workflow detects a user site and switches the base path automatically. You get only
one user site per account.

---

## Verifying a deployment

Check what is actually running rather than assuming a push arrived:

```bash
# Which commit is live? Compare with `git rev-parse --short=7 HEAD`.
curl -s https://portfolio-api-f06z.onrender.com/api/health/
# {"status":"ok","commit":"42d4851","debug":false}

# Is the frontend serving the app (not a Jekyll render of the README)?
curl -s https://khari759.github.io/django_profile/ | head -5

# Which API URL is baked into the live bundle?
JS=$(curl -s https://khari759.github.io/django_profile/ | grep -o '/django_profile/assets/[^"]*\.js' | head -1)
curl -s "https://khari759.github.io$JS" | grep -o 'https://[a-z0-9.-]*onrender[a-z.]*' | head -1

# Does CORS allow the frontend origin?
curl -s -D - -o /dev/null https://portfolio-api-f06z.onrender.com/api/overview/ \
  -H "Origin: https://khari759.github.io" | grep -i access-control-allow-origin
```

`debug` must be `false` in production. If it is `true`, `DJANGO_DEBUG` is misconfigured
and error pages will leak internals.

---

## Troubleshooting

### The site shows "Portfolio unavailable"

The frontend cannot reach the API. In order of likelihood:

1. **The API is asleep.** Free Render services idle out; the first request takes 30–50
   seconds. Wait and reload.
2. **`VITE_API_BASE_URL` is wrong or missing.** Check the baked-in URL with the bundle
   command above. An unset GitHub Actions variable expands to an **empty string**, not
   undefined, which is why `resolveApiBaseUrl()` treats blank as unset.
3. **CORS.** Open the browser console. `blocked by CORS policy` means
   `DJANGO_CORS_ALLOWED_ORIGINS` on Render does not list the frontend origin exactly.
4. **Mixed content.** An HTTPS page cannot call `http://`. The API URL must be `https://`.

### Pages serves the README instead of the app

Pages is in "Deploy from a branch" mode, so GitHub is rendering the repo with Jekyll.
The workflow sets Actions mode itself via `enablement: true`; if it still happens, set
**Settings → Pages → Source → GitHub Actions** by hand.

### A push did not reach Render

Check `/api/health/` — if `commit` is not your `HEAD`, the deploy never landed. Then:

- **Settings → Build & Deploy → Branch** — must be `main`. A wrong branch here means no
  push will ever deploy, which is silent and easy to miss.
- **Settings → Build & Deploy → Auto-Deploy** — must be `Yes`.
- **Events tab** — look for a failed build and read its log.
- Otherwise: **Manual Deploy → Deploy latest commit** (free; unlike Shell).

If a `render.yaml` change is involved, deploying code is not enough — sync the Blueprint.

### Admin rejects the password

"Please enter the correct username and password for a staff account" means the account
does not exist or the password differs.

1. Confirm the running commit includes `ensure_superuser` (`/api/health/`).
2. Confirm all three `DJANGO_SUPERUSER_*` variables are set — the command silently
   skips if username or password is blank.
3. Redeploy and check the deploy log for `superuser: created` or `superuser: updated`.

Remember that the env var is re-applied on every boot: if you also changed the password
in the admin UI, the next deploy resets it to the variable's value.

### Contact emails never arrive

1. Check **admin → Contact messages** — if messages are there, storage works and only
   delivery is failing.
2. `CONTACT_NOTIFY_EMAIL` unset means no send is attempted at all.
3. Check the Render logs for `Failed to send contact notification` — send errors are
   logged and swallowed so a mail outage cannot lose a message.
4. With Gmail, `535 Username and Password not accepted` means a normal password was used
   instead of an App Password.

### Tests pass locally but CI fails

Run exactly what CI runs:

```bash
cd backend && ruff check . && ruff format --check . && pytest
cd frontend && npm run lint && npm run typecheck && npm run test && npm run build
```

Also check for a missing migration, which CI fails on:

```bash
cd backend && python manage.py makemigrations --check --dry-run
```

---

## Maintenance

### Free-tier limits worth planning around

| Limit | Effect | Mitigation |
| --- | --- | --- |
| Service sleeps after ~15 min idle | First visit waits 30–50 s | Render Starter ($7/mo), or a scheduled ping |
| Free PostgreSQL expires after 30 days | Database is dropped | Content and admin are recreated on boot; only contact messages are lost |
| Ephemeral filesystem | Uploaded avatars, CVs, screenshots vanish on redeploy | Commit them, or attach S3/Cloudinary |

**Export contact messages before the 30-day expiry** — they are the only data not
reproducible from code. Admin → Contact messages, or via the database.

### Updating content

Either edit in the admin (immediate, no deploy), or edit
`backend/portfolio/management/commands/seed_portfolio.py` and push (version controlled,
survives a database rebuild). Both are idempotent and can be mixed.

Anything you want to survive a database recreation belongs in the seed file.

### Routine checks

- `/api/health/` matches `HEAD` after each push
- `debug` is `false`
- CI is green on `main`
- Contact messages are not piling up unread

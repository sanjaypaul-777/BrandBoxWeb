# Zentra-Web (Django)

Public marketing site + account dashboard for **Zentra**.

This is a **separate** app from the Shopify embedded app in `../Zentra` (Node).

| Surface | Role | Typical URL |
|---------|------|-------------|
| **Marketing** (this repo) | Landing, login, signup, checkout | `zentra.com` |
| **Dashboard** (this repo) | After login — connect → install → AI build | `app.zentra.com` |
| **Admin** (this repo) | Staff / superuser editor | `/admin/` |
| **Zentra** (sibling) | Shopify OAuth, Admin API, AI Store Builder | tunnel / `app.zentra.com` |

They share **one Shopify Partner app** and (in production) **one Postgres database**.

## How folders work

| Layer | Folder | Job |
|-------|--------|-----|
| **Routes + logic** | `apps/` | `views.py`, `urls.py`, models |
| **HTML** | `templates/` | What the user sees |
| **CSS / images** | `static/` | Look & assets |
| **Settings** | `config/` | Django settings, Celery, Shopify helpers |

**Rule:** change copy in `templates/…`. Change behavior in `apps/…/views.py`.

## Who can see what

```text
PUBLIC
  /                 marketing landing
  /checkout         purchase (optional account)
  /login /signup /forgot

AFTER LOGIN
  /dashboard        connect → install guide → niche pick
  /dashboard/connect/   save pasted store domain
  /dashboard/install/   open Shopify OAuth (or demo)
  /dashboard/installed/ confirm app installed
  /builder/start/       start AI store build
  /builder/building/<id>/   progress UI
  /builder/success/<id>/    store live
  /dashboard/product-finder/  Product Finder (UI shell — backend later)
  /dashboard/imports/         My Imports (UI shell — backend later)
  /dashboard/my-imports/      alias → imports

STATUS / ERRORS
  404 / 500 custom glass pages (handler404 / handler500)
  Maintenance via MAINTENANCE_MODE + MAINTENANCE_ETA env flags
  DEBUG previews: /__debug__/404/ · /__debug__/500/ · /__debug__/maintenance/

STAFF / SUPERUSER
  /admin/           Django admin (users, shops, niches, builds)
```

> **Product Finder** reads the Winning Product Vault (Django SQL). **My Imports**
> are shop drafts in Django; Push goes through the Node Shopify app.
>
> **Errors:** never show raw exceptions to users. 500 pages show a `ZEN-500-…`
> reference that is logged with the real traceback for support.

## Project tree

```text
Zentra-Web/
├── manage.py
├── requirements.txt
├── .env.example
├── .env.local                 # local secrets (gitignored)
├── AGENTS.md / CLAUDE.md      # Cursor / agent notes
├── config/
│   ├── settings.py
│   ├── urls.py                # mounts apps + /admin/
│   ├── asgi.py / wsgi.py
│   ├── celery.py              # async builds (later)
│   ├── context_processors.py  # SHOPIFY_PARTNER_SIGNUP_URL, etc.
│   └── shopify.py             # normalize shop + OAuth install URL
├── apps/
│   ├── home/                  # landing `/`
│   ├── accounts/              # login, signup, logout, forgot, OAuth stubs
│   │   ├── forms.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── dashboard/             # connect → install → build UI
│   │   ├── models.py          # ShopConnection
│   │   ├── views.py           # home, connect, install, mark_installed
│   │   └── urls.py
│   ├── checkout/              # public checkout
│   │   ├── forms.py
│   │   └── views.py
│   └── builder/               # AI store build engine (web side)
│       ├── models.py          # NichePack, BuildJob
│       ├── niches.py          # niche catalog
│       ├── services.py        # progress runner (local sim → Node later)
│       ├── views.py           # start, building, status JSON, success
│       └── urls.py
├── templates/
│   ├── base.html
│   ├── home/index.html
│   ├── accounts/              # login, signup, forgot, _social_auth
│   ├── checkout/index.html
│   ├── dashboard/index.html   # sidebar shell + flow steps
│   └── builder/               # building.html, success.html
├── static/
│   ├── css/
│   │   ├── base.css           # Obsidian tokens
│   │   ├── home.css
│   │   ├── auth.css
│   │   ├── checkout.css
│   │   ├── dashboard.css
│   │   └── builder.css
│   ├── js/
│   │   ├── tailwind-theme.js
│   │   └── ai-engine-3d.js
│   └── images/
├── media/                     # user uploads (local)
└── docs/
    ├── copy.md
    ├── UI-Design-System.md
    └── WEBAPP-SHOPIFY-INTEGRATION.md
```

## Local setup

```bash
cd Zentra-Web
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env.local
python manage.py migrate
python manage.py createsuperuser   # for /admin/
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

- Sign up → lands on `/dashboard` (private)
- Admin → [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Set `SHOPIFY_APP_URL` to the **live Cloudflare tunnel** printed by `../Zentra` → `npm run dev`  
(e.g. `https://xxxx.trycloudflare.com`).  
`https://app.zentra.com` only works after you deploy that domain — it will show “site can’t be reached” locally.

### Shared database (later / production)

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/zentra
```

Use the **same** Postgres as Zentra. Local default is SQLite (`db.sqlite3`).

## How it connects to the Shopify app

1. User signs up / logs in (Django auth → `User` table).
2. On `/dashboard`, user pastes `store.myshopify.com` → `ShopConnection` saved → **install guide**.
3. **Install Zentra** opens `{SHOPIFY_APP_URL}/auth?shop=...` (Zentra Node OAuth).
4. Merchant approves permissions; Prisma `Session` saved in Zentra.
5. Webapp polls **`GET /dashboard/api/install-status/?shop=...`**, which calls Zentra  
   **`GET /api/install-status`** (shared `ZENTRA_INTERNAL_API_SECRET`).
6. Only when `installed: true` → niche picker unlocks → `/builder/start/` → progress → success.
7. Real theme/product push still runs in Zentra Node later; webapp owns the guided UI + job records.

See `docs/WEBAPP-SHOPIFY-INTEGRATION.md`.

## Next steps

1. Google / Apple / Facebook OAuth (UI stubs exist)
2. Wire build runner to Zentra Node Admin API (replace local progress sim)
3. Celery worker for long builds
4. Shared Postgres with Zentra in staging/prod
5. `apps/api/` only if Django and Node need HTTP APIs beyond redirects + shared DB

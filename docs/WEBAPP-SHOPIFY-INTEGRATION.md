# Zentra: Webapp + Shopify App Integration

> **Zentra-Web is Django (Python).** Canonical Shopify engine stays in `../Zentra` (Node).  
> Pair with `docs/UI-Design-System.md` for visual tokens.

**Purpose:** Context to keep the public webapp working with the existing Zentra Shopify app.

**Product name:** Zentra  
**Webapp:** Django — landing, auth, dashboard, checkout, `/admin/`  
**Shopify app:** Embedded admin (AI Store Builder, Product Finder, …) + OAuth  

---

## 1. One product, two surfaces

| Surface | Role | Stack | Typical URL |
|--------|------|-------|-------------|
| **Webapp** | Landing, login, dashboard, connect store, Django admin | **Django** | `zentra.com` / `app.zentra.com` |
| **Shopify app** | OAuth, Admin API, AI Store Builder, Product Finder | **Node (Zentra)** | Shopify Admin embed |

- Same Shopify Partner app (`client_id` / secrets)
- Same database in production (Postgres)
- Build **engine** can stay in Zentra Node; webapp `apps.builder` holds web-side niche/build job records and can call Node later

The webapp is the **front door**. The Shopify app is the **store engine**.

---

## 2. What already exists (Shopify app)

| Feature | Route / area | Notes |
|---------|--------------|--------|
| Dashboard | `/app` | Store metrics, readiness |
| AI Store Builder | `/app/build` | Niche themes, products, … |
| Product Finder | `/app/product-finder` | Search/import |
| My Imports | `/app/my-imports` | Edit / push |
| Settings | `/app/settings` | Store config |
| Shopify OAuth | `/auth/*` | Install + Prisma `Session` |

**Shop domain:** `brandbox-9804.myshopify.com`  
Admin URLs are parsed by Django `config/shopify.py`.

---

## 3. End-to-end user flow

```text
1. User lands on Django webapp
2. Sign up / log in (Django auth) → User in DB
3. Dashboard: connect store or create Shopify account
4. Redirect to Zentra Node `/auth?shop=...`
5. Session saved in Zentra; return to `/dashboard?shop=...`
6. Django saves ShopConnection(user, shop)
7. Merchant uses Builder / Product Finder in Shopify Admin
```

---

## 4. Authentication

### Webapp (Django)

- Username/password (Django `User`) — Google can be added later
- Staff / superuser → `/admin/` (Django admin)
- Dashboard views use `@login_required`

### Shopify (existing)

- OAuth via Zentra Node app
- Prisma `Session` (shop + token)

Both are required for the full product.

---

## 5. Shared database

```text
User (Django)
  └── ShopConnection (user, shop, installedAt)

Session / Build / PendingProduct (Zentra Prisma — same Postgres in prod)
```

Local Django default: **SQLite**. Production: set `DATABASE_URL` to the same Postgres as Zentra.

---

## 6. Django project map

| App | Responsibility |
|-----|----------------|
| `home` | Marketing landing |
| `accounts` | Login, signup, logout, forgot |
| `dashboard` | UI: connect store, status (not build engine) |
| `checkout` | Public checkout UI |
| `builder` | Niche packs, build jobs, future async builds (Celery) |
| `api` | **Not created yet** — only if Django ↔ Node need HTTP APIs |

---

## 7. OAuth handoff

1. Django `/dashboard` normalizes shop to `*.myshopify.com`.
2. Redirect to `{SHOPIFY_APP_URL}/auth?shop=...`.
3. After install, Zentra redirects to `{DASHBOARD_URL}?shop=...`.
4. Django writes `ShopConnection`.

---

## 8. Agent instructions

We are building **Zentra-Web in Django**. Do not reintroduce Next.js for this repo.

1. Read this doc + `README.md` + `docs/UI-Design-System.md`
2. Keep Shopify OAuth in `../Zentra`
3. Prefer shared DB + redirects over a new `api` app until needed
4. Put build **logic** in `apps.builder`, dashboard **UI** in `apps.dashboard`

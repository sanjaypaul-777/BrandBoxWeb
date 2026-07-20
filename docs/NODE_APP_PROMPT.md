# BrandBox Node app — implementation prompt

Copy everything below the line into the new Node BrandBox app chat.

---

You are implementing / finishing the BrandBox Node Shopify app that powers the Django marketing + dashboard app (BrandBoxWeb).

## Architecture (do not change this split)

- **Django (BrandBoxWeb)** owns: login/signup, ShopConnection, NichePack/BuildJob UI, Winning Product Vault (CatalogProduct), My Imports drafts (ShopImport), Product Hunter scraper.
- **Node (this app)** owns: Shopify OAuth + offline Admin session, theme/product store builds, niches engine data, PendingProduct tracker, productCreate / publish / push to Shopify.
- Django **never** stores Shopify Admin access tokens. All Shopify writes go through Node.
- Catalog browse / search stays in Django SQL. Do **not** add a product-search API for the vault unless asked.

Sibling local folders:

- Web: `../BrandBoxWeb` (Django on http://127.0.0.1:8000)
- Node: this repo (Shopify app + Cloudflare tunnel URL)

## Shared env (must match exactly)

Django `.env.local`:

```
SHOPIFY_APP_URL=https://YOUR-TUNNEL.trycloudflare.com
BRANDBOX_INTERNAL_API_SECRET=<same secret as Node>
```

Node `.env`:

```
BRANDBOX_INTERNAL_API_SECRET=<same secret as Django>
```

Auth for every internal route below:

- Header: `X-BrandBox-Internal-Secret: <secret>`
- Reject missing/wrong secret with `401` + `{ "error": "unauthorized" }`
- Do **not** accept `?secret=` query params
- User-Agent from Django: `BrandBox-Web/1.0` (optional to check)

OAuth entry Django redirects to:

```
{SHOPIFY_APP_URL}/auth/login?shop={shop}.myshopify.com
```

(Must start Shopify OAuth when `shop` is present — not an empty login form.)

Shop domains are always `*.myshopify.com` (normalized lowercase).

---

## Required internal APIs (JSON)

All successful responses should include `"ok": true`.

### 1) Install / connection — REQUIRED for Overview + Builder unlock

`GET /api/install-status?shop=store.myshopify.com`

Return:

```json
{
  "ok": true,
  "shop": "store.myshopify.com",
  "installed": true,
  "connected": true,
  "hasOfflineSession": true,
  "productsCount": 42,
  "productsCountAvailable": true,
  "statusKey": "connected_with_products",
  "statusCopy": "42 products live",
  "checkedAt": "ISO-8601"
}
```

Rules:

- `installed` / `connected` / `hasOfflineSession` = true only when offline Admin session exists.
- `productsCount` must be `null` when unknown — **never** fake `0`.
- Set `productsCountAvailable: false` when count unknown.
- On auth failure: 401. On shop unknown / not installed: 200 with `installed:false` (preferred) rather than opaque 500.

`statusKey` values Django understands:

`not_connected` | `connected_count_unavailable` | `connected_empty` | `connected_with_products`

### 2) Niches — REQUIRED for builder counts / theme names

`GET /api/niches`

Return:

```json
{
  "ok": true,
  "niches": [
    {
      "webSlug": "living",
      "nicheId": "living",
      "themeName": "BrandBox Living",
      "productCount": 20
    }
  ]
}
```

Django niche slugs (`webSlug` must match):

`living`, `peak`, `care`, `junior`, `paws`, `lux`, `tech`, `vogue`, `mart`, `pod`

(`pod` may be 0 products.)

### 3) Store build engine — REQUIRED for AI Store Builder

`POST /api/build/start`  
Body: `{ "shop": "store.myshopify.com", "nicheId": "care" }`  
(`nicheId` is the web slug.)

Success:

```json
{
  "ok": true,
  "buildId": "cuid-or-uuid",
  "status": "running",
  "progress": 0,
  "currentStep": 0,
  "stepLabel": "Preparing theme…",
  "productCount": 0
}
```

If app not installed: `{ "ok": false, "error": "app_not_installed" }` (Django maps this to a user message).

`GET /api/build/status?shop=...&buildId=...`  
(This poll may also **advance** the build on Node.)

While running / done / failed:

```json
{
  "ok": true,
  "buildId": "...",
  "status": "running|completed|failed",
  "completed": false,
  "failed": false,
  "progress": 0-100,
  "currentStep": 0,
  "stepLabel": "human label",
  "productCount": 12,
  "error": null
}
```

Django UI maps progress to 3 steps:

- step 0 / progress < 15 → “theme”
- step 1 / progress < 50 → middle
- else → final; progress 100 or `completed:true` → success page

`POST /api/build/retry`  
Body: `{ "shop": "...", "buildId": "oldId" }`  
Return a **new** `buildId` for the same niche (same shape as start).

Build engine responsibilities on Node:

- Apply niche theme to the shop
- Load niche products into Shopify
- Persist build row keyed by `buildId`
- Use offline Admin token only on Node

### 4) Imports / Push — REQUIRED for My Imports → Shopify

Django owns drafts. Node owns live tracker + Admin push.

`GET /api/imports?shop=...`  
Optional `status` query.

Return:

```json
{
  "ok": true,
  "imports": [
    {
      "id": "node-pending-id",
      "sourceId": "vault-source-id",
      "status": "imported|in_store|removed_from_store|available|published|removed",
      "shopifyProductId": "gid://shopify/Product/123 or numeric",
      "title": "..."
    }
  ]
}
```

Django matches rows by `sourceId` and syncs status / shopifyProductId / node id onto `ShopImport`.

`POST /api/imports` — upsert PendingProduct before publish  
Body (Django sends):

```json
{
  "shop": "store.myshopify.com",
  "sourceId": "...",
  "title": "...",
  "cost": "10.00",
  "sellPrice": "30.00",
  "compareAtPrice": "49.00",
  "description": "...",
  "category": "...",
  "source": "https://product-url...",
  "imageUrl": "https://..."
}
```

Return:

```json
{
  "ok": true,
  "import": { "id": "node-id", "sourceId": "...", "status": "imported" }
}
```

`POST /api/imports/:id/publish`  
Body: `{ "shop": "store.myshopify.com" }`

Must:

1. Create/update Shopify product via Admin API (title, images, description)
2. Set sell / compare-at / inventory / sales channels as designed
3. Return:

```json
{
  "ok": true,
  "shopifyProductId": "...",
  "import": {
    "id": "node-id",
    "sourceId": "...",
    "status": "in_store",
    "shopifyProductId": "..."
  }
}
```

Prices from Django are **USD dollars** (e.g. `12.99`), not cents.

---

## What Django does NOT need from Node

- Product vault search (Django `CatalogProduct`)
- User accounts / JWT for BrandBox login
- Storing web BuildJob rows (Django has `BuildJob.brandbox_build_id`)

## Local bring-up checklist

1. Node: `npm run dev` / Shopify CLI → copy Cloudflare URL
2. Paste into Django `SHOPIFY_APP_URL`
3. Same `BRANDBOX_INTERNAL_API_SECRET` on both
4. Django: `python manage.py runserver`
5. Flow to verify:
   - Connect shop → Install → `/api/install-status` shows installed
   - Builder niche → start → poll `/api/build/status` → success
   - Product Hunter import (Django only) → My Imports → Push → `/api/imports` + publish → product on Shopify

## Implementation goals

Make all of the routes above operational end-to-end with real Shopify Admin calls (not stubs). Prefer clear JSON errors (`error`, optional `message`) and stable `buildId` / import `id` values. Match header + env names exactly so BrandBoxWeb works without code changes on the Django side.

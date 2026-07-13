# Winning Product Vault + Product Hunter (Django admin)

## What this does

- **Product Hunter** — run Meta Ads → Shopify product hunts from admin (**Start Hunting**)
- **Winning Product Vault** — Django mirror of hunted products
- Also writes to **Google Sheet** (Node Product Finder keeps reading this)

## Admin

1. Install deps: `pip install -r requirements.txt`
2. Ensure `secrets/google-sheets-sa.json` exists (service account with Editor on the sheet)
3. `python manage.py migrate`
4. Open `/admin/` → **Winning Product Vault** → **Product Hunter** → **Start Hunting**
   - Mode: Single query / All niches / Sync from sheet / Clean duplicates / Fill ids / **Purge dead (404)**
   - Save → job runs in background; refresh to read the log
5. **Winning Product Vault** — browse hunted products

Dead products (404 source page or no live images) are **never stored**. New hunts skip them; use **Purge dead** to remove ones already in the vault.

## CLI

```bash
python manage.py scrape_products --sync-sheet          # Sheet → DB (skips dead)
python manage.py scrape_products -q skincare -c US -n 30
python manage.py scrape_products --all-niches -n 200
python manage.py scrape_products --clean-dupes
python manage.py scrape_products --purge-dead          # Drop vault rows with 404 source/images
```

## Settings (`.env.local`)

```
CATALOG_SPREADSHEET_ID=1RiqcsWpY0mDPMjh5gZ7RcDvQkVGwbAr9nHo54ENUTac
CATALOG_SHEET_TAB=Meta Ads Products
CATALOG_SERVICE_ACCOUNT_FILE=  # default secrets/google-sheets-sa.json
```

## Stable `id` column

Sheet column **A** is `id` (`zp_<hash>` from Product URL).

```bash
python manage.py scrape_products --fill-ids   # backfill + sync DB
```

New scrapes write `id` automatically. Node `datasheetStorage` reads `id` as `sourceId`.

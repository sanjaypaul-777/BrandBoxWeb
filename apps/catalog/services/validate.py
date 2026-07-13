"""Reject / purge catalog rows whose source or images no longer exist (HTTP 404)."""

from __future__ import annotations

from collections.abc import Callable
from urllib.parse import urlparse

import httpx

from apps.dashboard.catalog import _image_candidates_from_row, _normalize_image_url

LogFn = Callable[[str], None]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
}


def url_exists(url: str, *, timeout: float = 8.0, client: httpx.Client | None = None) -> bool:
    """True if URL returns a successful response (2xx/3xx)."""
    url = _normalize_image_url(url)
    if not url:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return False
    except Exception:
        return False

    own = client is None
    if own:
        client = httpx.Client(timeout=timeout, follow_redirects=True, headers=_HEADERS)
    assert client is not None
    try:
        try:
            resp = client.head(url)
            if resp.status_code in (405, 403, 400):
                resp = client.get(url)
        except httpx.HTTPError:
            resp = client.get(url)
        return 200 <= resp.status_code < 400
    except Exception:
        return False
    finally:
        if own:
            client.close()


def first_live_image(urls: list[str], *, client: httpx.Client | None = None) -> str:
    """Return first image URL that still loads, else ''."""
    own = client is None
    if own:
        client = httpx.Client(timeout=8.0, follow_redirects=True, headers=_HEADERS)
    assert client is not None
    try:
        for u in urls:
            if url_exists(u, client=client):
                return _normalize_image_url(u)
        return ""
    finally:
        if own:
            client.close()


def product_is_storable(
    *,
    product_url: str,
    feature_image: str = "",
    product_images: str = "",
    client: httpx.Client | None = None,
    require_product_page: bool = True,
) -> tuple[bool, str, str]:
    """
    Returns (ok, live_feature_image, reason).
    Requires at least one live image; optionally a live product page.
    """
    own = client is None
    if own:
        client = httpx.Client(timeout=8.0, follow_redirects=True, headers=_HEADERS)
    assert client is not None
    try:
        class _Row:
            pass

        row = _Row()
        row.feature_image = feature_image
        row.product_images = product_images
        candidates = _image_candidates_from_row(row)
        live_img = first_live_image(candidates, client=client)
        if not live_img:
            return False, "", "no_live_image"

        if require_product_page and product_url:
            if not url_exists(product_url, client=client):
                return False, "", "product_page_404"

        return True, live_img, ""
    finally:
        if own:
            client.close()


def purge_dead_vault_products(*, log: LogFn | None = None) -> int:
    """Delete CatalogProduct rows with dead images / product pages. Returns deleted count."""
    from django.db import close_old_connections

    from apps.catalog.models import CatalogProduct, ShopImport

    def _log(msg: str) -> None:
        if log:
            log(msg)

    # Snapshot PKs first — SQLite + long HTTP checks cannot keep an iterator open.
    pks = list(CatalogProduct.objects.values_list("pk", flat=True))
    total = len(pks)
    _log(f"[*] Checking {total} vault product(s) for dead sources/images…")

    deleted = 0
    checked = 0
    client = httpx.Client(timeout=8.0, follow_redirects=True, headers=_HEADERS)
    try:
        for pk in pks:
            close_old_connections()
            row = CatalogProduct.objects.filter(pk=pk).first()
            if row is None:
                continue
            checked += 1
            ok, live_img, reason = product_is_storable(
                product_url=row.product_url or "",
                feature_image=row.feature_image or "",
                product_images=row.product_images or "",
                client=client,
            )
            if ok:
                if live_img and live_img != (row.feature_image or ""):
                    row.feature_image = live_img[:1000]
                    row.save(update_fields=["feature_image", "updated_at"])
            else:
                _log(f"   [-] drop {row.source_id}: {reason} · {(row.title or '')[:40]}")
                ShopImport.objects.filter(source_id=row.source_id).delete()
                row.delete()
                deleted += 1
            if checked % 25 == 0:
                _log(f"   …checked {checked}/{total} (purged {deleted})")
    finally:
        client.close()
    _log(f"[DONE] Purged {deleted} dead product(s) from Winning Product Vault")
    return deleted

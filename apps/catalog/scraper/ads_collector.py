"""Meta Ads Library collector - extracts ads with landing page URLs."""

from urllib.parse import urlparse

from meta_ads_collector import MetaAdsCollector
from meta_ads_collector.constants import STATUS_ACTIVE

from .config import EXCLUDED_DOMAINS


def _normalize_url(url: str) -> str | None:
    if not url or not url.strip():
        return None
    return url.strip()


def _is_excluded_domain(url: str) -> bool:
    try:
        parsed = urlparse(url)
        domain = (parsed.netloc or "").lower()
        if domain.startswith("www."):
            domain = domain[4:]
        for excluded in EXCLUDED_DOMAINS:
            if excluded in domain or domain.endswith("." + excluded):
                return True
        return False
    except Exception:
        return True


def collect_landing_pages(
    search_terms: str,
    country: str = "US",
    max_ads: int = 200,
) -> list[dict]:
    results = []
    seen_urls = set()

    with MetaAdsCollector(rate_limit_delay=1.5, timeout=20) as collector:
        for ad in collector.search(
            query=search_terms,
            country=country,
            status=STATUS_ACTIVE,
            max_results=max_ads,
        ):
            for creative in getattr(ad, "creatives", []) or []:
                link_url = getattr(creative, "link_url", None) or getattr(
                    creative, "link", None
                )
                if not link_url:
                    continue

                url = _normalize_url(link_url)
                if not url or _is_excluded_domain(url):
                    continue

                url_key = url.split("?")[0].rstrip("/")
                if url_key in seen_urls:
                    continue
                seen_urls.add(url_key)

                page_name = ""
                if ad.page:
                    page_name = getattr(ad.page, "name", "") or ""

                results.append(
                    {
                        "ad_id": getattr(ad, "id", ""),
                        "page_name": page_name,
                        "landing_url": url,
                        "ad_snapshot_url": getattr(ad, "ad_snapshot_url", "")
                        or getattr(ad, "snapshot_url", ""),
                    }
                )

                if len(results) >= max_ads:
                    return results

    return results

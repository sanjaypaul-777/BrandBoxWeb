"""Shopify store detection and product data extraction."""

import json
import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

from .config import REQUEST_TIMEOUT
from apps.catalog.services.money import (
    normalize_compare_usd,
    normalize_price_usd,
    pick_offer_price_and_currency,
)

# Shopify detection signals
SHOPIFY_SIGNALS = [
    "cdn.shopify.com",
    "Shopify.theme",
    "shopifycdn.net",
    "myshopify.com",
    "/cdn/shop/",
    "shopify-section",
]


def is_shopify_store(html: str, url: str = "") -> bool:
    """Detect if page is a Shopify store using multiple signals."""
    html_lower = html.lower()
    url_lower = url.lower()

    # Check URL for myshopify
    if "myshopify.com" in url_lower:
        return True

    # Count matching signals
    matches = sum(1 for sig in SHOPIFY_SIGNALS if sig.lower() in html_lower or sig in html)
    return matches >= 2


def _get_base_url(url: str) -> str:
    """Extract base URL (scheme + netloc) from full URL."""
    parsed = urlparse(url)
    return f"{parsed.scheme or 'https'}://{parsed.netloc}"


def fetch_page(url: str) -> tuple[str, str]:
    """Fetch page HTML. Returns (html, final_url)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text, str(resp.url)


def get_product_urls_from_shopify(landing_url: str) -> list[str]:
    """
    Get product page URLs from a Shopify store.
    Tries: products.json API, sitemap, or parses landing page for product links.
    """
    base_url = _get_base_url(landing_url)
    product_urls = []

    # Method 1: products.json - fastest, most reliable
    try:
        products_json_url = urljoin(base_url, "/products.json?limit=250")
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            resp = client.get(products_json_url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                for product in data.get("products", []):
                    handle = product.get("handle")
                    if handle:
                        product_urls.append(urljoin(base_url, f"/products/{handle}"))
                if product_urls:
                    return product_urls[:50]  # Limit to 50 products per store
    except Exception:
        pass

    # Method 2: Fetch landing page and check if it's a product page
    try:
        html, final_url = fetch_page(landing_url)
        soup = BeautifulSoup(html, "html.parser")

        # If landing page is already a product page, extract its URL
        if "/products/" in final_url:
            product_urls.append(final_url.split("?")[0])
            return product_urls

        # Find product links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/products/" in href and "cdn.shopify.com" not in href:
                full_url = urljoin(base_url, href)
                full_url = full_url.split("?")[0]
                if full_url not in product_urls:
                    product_urls.append(full_url)
                    if len(product_urls) >= 50:
                        break
    except Exception:
        pass

    return product_urls[:50]


# Signals for best-selling / viral products (case-insensitive)
BESTSELLER_SIGNALS = [
    "bestseller", "best-seller", "best seller", "#1 seller", "top seller",
    "featured", "popular", "viral", "trending", "staff pick", "editor's pick",
    "best seller", "bestselling", "most popular", "customer favorite",
]


def _score_product_for_virality(product: dict, base_url: str) -> tuple[int, str]:
    """
    Score a product for best-selling/viral likelihood.
    Returns (score, product_url). Higher score = more likely viral/bestseller.
    """
    raw_tags = product.get("tags")
    if isinstance(raw_tags, list):
        tags = " ".join(str(t) for t in raw_tags).lower()
    else:
        tags = (raw_tags or "").lower()
    title = (product.get("title") or "").lower()
    handle = product.get("handle", "")
    product_url = f"{base_url.rstrip('/')}/products/{handle}" if handle else ""

    score = 0
    combined = f"{tags} {title}"

    for signal in BESTSELLER_SIGNALS:
        if signal in combined:
            score += 10 if signal in ("bestseller", "best-seller", "viral", "#1 seller") else 5

    # Bonus: more variants often = popular product
    variants = product.get("variants", [])
    if len(variants) > 3:
        score += 2

    # Bonus: has compare_at_price = likely on sale / promoted
    for v in variants[:1]:
        if v.get("compare_at_price") and str(v.get("compare_at_price")) != "0.0":
            score += 3
        break

    return score, product_url


def get_top_products_from_store(
    landing_url: str,
    max_products: int = 10,
    country: str | None = None,
) -> list[dict]:
    """
    Get up to max_products top-performing (best-selling/viral) products from a Shopify store.
    Returns list of product dicts sorted by virality score. Prices converted to USD.
    """
    base_url = _get_base_url(landing_url)
    results: list[dict] = []

    # Fetch products.json first (for enrichment + scoring)
    try:
        products_json_url = urljoin(base_url, "/products.json?limit=250")
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            resp = client.get(products_json_url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return results[:max_products]
            data = resp.json()
    except Exception:
        return results[:max_products]

    products = data.get("products", [])

    # Case 1: Landing page is a product page - include it first
    try:
        html, final_url = fetch_page(landing_url)
        if "/products/" in final_url:
            product_url = final_url.split("?")[0]
            handle = product_url.rstrip("/").split("/products/")[-1]
            product_json = next((p for p in products if p.get("handle") == handle), None)
            prod = extract_product_data(
                product_url,
                pre_fetched_html=html,
                product_json=product_json,
                country=country,
            )
            if prod and (prod.get("title") or prod.get("price")):
                results.append(prod)
    except Exception:
        pass

    if not products:
        return results[:max_products]

    scored: list[tuple[int, str]] = []
    for p in products:
        score, url = _score_product_for_virality(p, base_url)
        if url:
            scored.append((score, url))

    scored.sort(key=lambda x: (-x[0], x[1]))

    seen_urls = {r.get("product_url") for r in results}
    # Build handle -> product_json for enrichment
    product_by_handle = {p.get("handle"): p for p in products if p.get("handle")}

    for _, url in scored:
        if len(results) >= max_products:
            break
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        handle = url.rstrip("/").split("/products/")[-1].split("?")[0] if "/products/" in url else ""
        product_json = product_by_handle.get(handle) if handle else None
        prod = extract_product_data(url, product_json=product_json, country=country)
        if prod and (prod.get("title") or prod.get("price")):
            results.append(prod)

    return results


def extract_product_data(
    product_url: str,
    pre_fetched_html: str | None = None,
    product_json: dict | None = None,
    country: str | None = None,
) -> dict | None:
    """
    Extract product data from a Shopify product page.
    Prices are converted to USD before return (catalog stores USD only).
    """
    try:
        if pre_fetched_html:
            html = pre_fetched_html
        else:
            html, _ = fetch_page(product_url)
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "product_url": product_url,
            "title": "",
            "price": "",
            "compare_price": "",
            "currency": "",
            "ratings": "",
            "review_count": "",
            "product_images": "",
            "feature_image": "",
            "category": "",
            "description": "",
        }

        # Enrich from products.json (compare_price, product_type) - most reliable
        if product_json:
            for v in product_json.get("variants", [])[:1]:
                cp = v.get("compare_at_price")
                if cp and str(cp) not in ("0", "0.0", "None", ""):
                    result["compare_price"] = str(cp)
                break
            if product_json.get("product_type"):
                result["category"] = str(product_json["product_type"])

        # Method 1: JSON-LD structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, dict):
                    if data.get("@type") == "Product":
                        result["title"] = result["title"] or data.get("name", "")
                        result["description"] = (
                            data.get("description", "")[:2000]
                            if data.get("description")
                            else ""
                        )
                        offers = data.get("offers", {})
                        if isinstance(offers, dict):
                            cur = str(offers.get("priceCurrency") or "").upper()
                            if cur:
                                result["currency"] = result["currency"] or cur
                            if not result["price"] and offers.get("price") not in (None, ""):
                                result["price"] = str(offers.get("price", ""))
                        elif isinstance(offers, list) and offers:
                            price, cur = pick_offer_price_and_currency(offers)
                            if price and not result["price"]:
                                result["price"] = price
                            if cur:
                                result["currency"] = result["currency"] or cur
                        if "image" in data:
                            imgs = data["image"]
                            if isinstance(imgs, str):
                                result["feature_image"] = result["feature_image"] or imgs
                                result["product_images"] = result["product_images"] or imgs
                            elif isinstance(imgs, list):
                                result["product_images"] = result["product_images"] or "|".join(
                                    img if isinstance(img, str) else img.get("url", "")
                                    for img in imgs[:10]
                                )
                                if not result["feature_image"] and imgs:
                                    result["feature_image"] = (
                                        imgs[0] if isinstance(imgs[0], str) else imgs[0].get("url", "")
                                    )
                        agg = data.get("aggregateRating", {})
                        if agg:
                            result["ratings"] = str(agg.get("ratingValue", ""))
                            result["review_count"] = str(agg.get("reviewCount", ""))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            result["title"] = result["title"] or item.get("name", "")
                            result["description"] = (
                                (item.get("description", "") or "")[:2000]
                            )
                            offers = item.get("offers", {})
                            if isinstance(offers, dict):
                                cur = str(offers.get("priceCurrency") or "").upper()
                                if cur:
                                    result["currency"] = result["currency"] or cur
                                result["price"] = result["price"] or str(offers.get("price", ""))
                            elif isinstance(offers, list) and offers:
                                price, cur = pick_offer_price_and_currency(offers)
                                result["price"] = result["price"] or price
                                if cur:
                                    result["currency"] = result["currency"] or cur
                            if "image" in item:
                                imgs = item["image"]
                                if isinstance(imgs, list) and imgs:
                                    result["feature_image"] = result["feature_image"] or (
                                        imgs[0] if isinstance(imgs[0], str) else imgs[0].get("url", "")
                                    )
                                    result["product_images"] = result["product_images"] or "|".join(
                                        i if isinstance(i, str) else i.get("url", "")
                                        for i in imgs[:10]
                                    )
                            agg = item.get("aggregateRating", {})
                            if agg:
                                result["ratings"] = str(agg.get("ratingValue", ""))
                                result["review_count"] = str(agg.get("reviewCount", ""))
                            break
            except json.JSONDecodeError:
                continue

        # Method 2: Shopify product JSON in script tag (compare_at_price, variants)
        for script in soup.find_all("script"):
            s = script.string or ""
            if "product" not in s.lower():
                continue
            # Match variant compare_at_price
            for m in re.finditer(r'"compare_at_price":\s*([0-9.]+)', s):
                val = m.group(1)
                if val and val not in ("0", "0.0"):
                    result["compare_price"] = result["compare_price"] or val
                    break
            for m in re.finditer(r'compare_at_price["\']?\s*:\s*["\']?([0-9.]+)', s):
                val = m.group(1)
                if val and val not in ("0", "0.0"):
                    result["compare_price"] = result["compare_price"] or val
                    break
            # Match product JSON
            match = re.search(r'"product":\s*(\{[^}]+\})', s)
            if match:
                try:
                    prod = json.loads(match.group(1))
                    result["title"] = result["title"] or prod.get("title", "")
                    for v in prod.get("variants", [])[:1]:
                        result["price"] = result["price"] or str(v.get("price", ""))
                        cp = v.get("compare_at_price")
                        if cp and str(cp) not in ("0", "0.0"):
                            result["compare_price"] = result["compare_price"] or str(cp)
                    if not result["feature_image"] and prod.get("featured_image"):
                        result["feature_image"] = prod["featured_image"]
                except json.JSONDecodeError:
                    pass

        # Method 3: Review count from Judge.me, Loox, Stamped widgets
        for el in soup.find_all(attrs={"data-number-of-reviews": True}):
            result["review_count"] = result["review_count"] or el.get("data-number-of-reviews", "")
        for el in soup.find_all(class_=re.compile(r"jdgm-rev-widg|loox-rating|stamped")):
            count_el = el.find(string=re.compile(r"\(\s*\d+\s*reviews?\s*\)|^\d+\s*reviews?$", re.I))
            if count_el:
                nums = re.findall(r"\d+", count_el)
                if nums:
                    result["review_count"] = result["review_count"] or nums[0]
        # data-reviews-count, data-review-count
        for el in soup.find_all(attrs=True):
            for k, v in el.attrs.items():
                if "review" in k.lower() and "count" in k.lower() and str(v).isdigit():
                    result["review_count"] = result["review_count"] or str(v)
                    break

        # Method 4: Meta tags
        result["title"] = result["title"] or (
            (og := soup.find("meta", property="og:title")) and og.get("content") or ""
        )
        if not result["feature_image"]:
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                result["feature_image"] = og_image["content"]
        # product_type meta
        pt_meta = soup.find("meta", property="product:category") or soup.find("meta", {"name": "product_type"})
        if pt_meta and pt_meta.get("content") and not result["category"]:
            result["category"] = pt_meta["content"]

        # Method 5: Price from HTML
        if not result["price"]:
            price_el = (
                soup.find("span", class_=re.compile(r"price|money"))
                or soup.find(class_=re.compile(r"product-price"))
                or soup.find("span", {"data-product-price": True})
            )
            if price_el:
                result["price"] = price_el.get_text(strip=True)

        # Compare price from HTML (was $X, compare at, original price)
        if not result["compare_price"]:
            for el in soup.find_all(class_=re.compile(r"compare|was|original|sale-price")):
                text = el.get_text(strip=True)
                money = re.search(r"[\$£€]?\s*[\d,]+\.?\d*", text)
                if money:
                    result["compare_price"] = money.group(0).strip()
                    break

        # Breadcrumb / collection for category
        if not result["category"]:
            nav = soup.find("nav", {"aria-label": "breadcrumb"}) or soup.find(class_=re.compile(r"breadcrumb"))
            if nav:
                links = nav.find_all("a")
                if len(links) >= 2:
                    result["category"] = links[-2].get_text(strip=True)
            if not result["category"]:
                coll_link = soup.find("a", href=re.compile(r"/collections/"))
                if coll_link:
                    result["category"] = coll_link.get_text(strip=True)

        # Convert any currency → USD, fix Shopify cents; catalog stores USD only
        cur = result.get("currency") or ""
        raw_price = result.get("price") or ""
        raw_compare = result.get("compare_price") or ""
        result["price"] = normalize_price_usd(
            raw_price, "", currency=cur or None, country=country
        )
        result["compare_price"] = normalize_compare_usd(
            raw_compare,
            cost=raw_price,
            currency=cur or None,
            country=country,
        )
        result["currency"] = "USD"

        return result if result["title"] or result["price"] else None

    except Exception:
        return None

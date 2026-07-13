"""Scraper defaults — Sheet ID / credentials come from Django settings."""

from pathlib import Path

# Domains to exclude from landing page crawling
EXCLUDED_DOMAINS = {
    "amazon.com",
    "amazon.co.uk",
    "amazon.in",
    "flipkart.com",
    "etsy.com",
}

TARGET_ROWS = 100
PRODUCTS_PER_STORE = 10
REQUEST_TIMEOUT = 15
MAX_CONCURRENT_REQUESTS = 5
DELAY_BETWEEN_REQUESTS = 1.0

NICHES = [
    "home decor",
    "kitchen",
    "garden",
    "skincare",
    "baby",
    "toy",
    "pet",
    "fitness",
    "jewellery",
    "electronics",
    "fashion",
    "cloth",
    "general",
]

COUNTRIES = {
    "US": "USA",
    "CA": "Canada",
    "IN": "India",
    "GB": "UK",
}

# Package root (for optional local credentials fallback)
SCRAPER_DIR = Path(__file__).resolve().parent

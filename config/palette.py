"""
config/palette.py — BrandBox brand colors for Python code.

Mirror of tokens in static/css/base.css :root.
Edit hex values here AND in base.css together.
"""

from __future__ import annotations

# —— Brand palette (match base.css) ——
BLACK = "#000000"
INK = "#06101a"
MIDNIGHT = "#0d172f"
MAGENTA = "#ff00e5"
GREEN = "#4edea3"
CANVAS = "#EEF2F8"
OFF_WHITE = "#fefefe"  # near-white — use this, never raw #fefefe
WHITE = "#ffffff"

# —— Named neutrals (match base.css) ——
FOG = "#e5e7eb"  # light border / form chrome (was unnamed Tailwind gray-200)

# NichePack.accent seed cycle (DB field; UI uses theme images, not these colors)
ACCENTS = (GREEN, MAGENTA, MIDNIGHT, INK)

"""One-shot: inject section-local CSS token blocks. Run from repo root."""
from __future__ import annotations

import re
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "static" / "css"


def patch_selector_block(text: str, selector: str, new_block: str) -> str:
    """Replace first `{...}` block for exact selector like `.catalog` or `.ms`."""
    pattern = re.compile(
        rf"(?m)^{re.escape(selector)}\s*\{{",
    )
    m = pattern.search(text)
    if not m:
        raise SystemExit(f"selector not found: {selector}")
    start = m.start()
    brace = text.find("{", m.end() - 1)
    depth = 0
    i = brace
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                return text[:start] + new_block.rstrip() + text[end:]
        i += 1
    raise SystemExit(f"unclosed block for {selector}")


def patch_header(text: str, header: str) -> str:
    return re.sub(r"^/\*[\s\S]*?\*/", header.rstrip(), text, count=1)


FILES: dict[str, list[tuple[str, str]]] = {}

HEADERS = {
    "stores.css": """
/**
 * stores.css — My Stores + store detail ONLY.
 *
 * Edit look via --ms-* on .ms (never :root for this page).
 *
 * Sections: .ms | .ms-row* | .ms-menu* | .ms-empty*
 */
""".strip(),
    "settings.css": """
/**
 * settings.css — Settings page ONLY.
 *
 * Edit look via --st-* on .st (never :root for this page).
 *
 * Sections: .st | .st-card* | .st-toggle* | .st-danger*
 */
""".strip(),
    "auth.css": """
/**
 * auth.css — Login / Signup / Forgot / Password change ONLY.
 *
 * Edit look via --auth-* on .auth-page (never :root for this page).
 *
 * Sections: .auth-page | .auth-card | .auth-submit | .auth-social* | .auth-footer*
 */
""".strip(),
    "checkout.css": """
/**
 * checkout.css — Checkout page ONLY.
 *
 * Edit look via --checkout-* on .checkout (never :root for this page).
 *
 * Sections: .checkout | .checkout-form* | .checkout-summary*
 */
""".strip(),
    "status.css": """
/**
 * status.css — 404 / 500 / maintenance / build-failed ONLY.
 *
 * Edit look via --status-* on .status-page (never :root for this page).
 *
 * Sections: .status-page* | .status-card* | .build-error*
 */
""".strip(),
    "contact.css": """
/**
 * contact.css — Contact page ONLY (shell from auth.css).
 *
 * Edit look via --contact-* on .contact-page (never :root for this page).
 */
""".strip(),
    "builder.css": """
/**
 * builder.css — AI Store Builder wizard + building/success ONLY.
 *
 * Edit look via --ab-* on .ab and --build-* on .build-page (never :root).
 *
 * Sections: .ab-* | .build-page* | .build-card*
 */
""".strip(),
    "home.css": """
/**
 * home.css — Marketing homepage sections ONLY.
 *
 * Edit look via --home-* on .brandbox-home and section tokens
 * (--hero-*, --nav-*, …). Never restyle homepage from :root.
 *
 * Sections: .brandbox-nav* | .brandbox-hero* | .brandbox-how* | .brandbox-niches*
 *           .brandbox-pricing* / .brandbox-launch* | .brandbox-footer*
 *           .brandbox-newsletter* | .brandbox-btn* (shared btn uses brand tokens)
 */
""".strip(),
}


def section_tokens(
    prefix: str,
    *,
    bg: str = "transparent",
    text: str = "#dde4dd",
    muted: str = "#bbcabf",
    surface: str = "#1a211d",
    surface_high: str = "#242c27",
    input_bg: str = "#0a0a0c",
    hairline: str = "rgba(255, 255, 255, 0.1)",
    outline: str = "#3c4a42",
    outline_soft: str = "#86948a",
    primary: str = "#4edea3",
    on_primary: str = "#003824",
    primary_container: str = "#10b981",
    primary_fixed: str = "#6ffbbe",
    error: str = "#ffb4ab",
    glass: str = "rgba(29, 28, 36, 0.6)",
    navy: str = "#1d1c24",
    accent: str = "#ff00e5",
    purple: str = "#ad7bff",
    extra: str = "",
    layout: str = "",
) -> str:
    p = prefix
    return f"""
  /* —— Section tokens (edit here only) —— */
  --{p}-bg: {bg};
  --{p}-text: {text};
  --{p}-muted: {muted};
  --{p}-surface: {surface};
  --{p}-surface-high: {surface_high};
  --{p}-input-bg: {input_bg};
  --{p}-hairline: {hairline};
  --{p}-outline: {outline};
  --{p}-outline-soft: {outline_soft};
  --{p}-primary: {primary};
  --{p}-on-primary: {on_primary};
  --{p}-primary-container: {primary_container};
  --{p}-primary-fixed: {primary_fixed};
  --{p}-error: {error};
  --{p}-glass: {glass};
  --{p}-navy: {navy};
  --{p}-accent: {accent};
  --{p}-purple: {purple};
{extra}
  /* Bridge: children using shared names stay section-scoped */
  --background: var(--{p}-bg);
  --on-surface: var(--{p}-text);
  --on-background: var(--{p}-text);
  --on-surface-variant: var(--{p}-muted);
  --surface-container: var(--{p}-surface);
  --surface-container-high: var(--{p}-surface-high);
  --deep-obsidian: var(--{p}-input-bg);
  --surface-navy: var(--{p}-navy);
  --hairline: var(--{p}-hairline);
  --outline-variant: var(--{p}-outline);
  --outline: var(--{p}-outline-soft);
  --primary: var(--{p}-primary);
  --on-primary: var(--{p}-on-primary);
  --primary-container: var(--{p}-primary-container);
  --primary-fixed: var(--{p}-primary-fixed);
  --error: var(--{p}-error);
  --glass: var(--{p}-glass);
  --accent-pink: var(--{p}-accent);
  --vibrant-purple: var(--{p}-purple);
{layout}""".rstrip()


# stores
FILES["stores.css"] = [
    (
        ".ms",
        f""".ms {{
{section_tokens("ms", extra='''  --ms-mint: #4edea3;
  --ms-magenta: #ff00e5;
  --ms-max: 1280px;
''', layout='''
  max-width: var(--ms-max);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 21.6px;
  font-family: var(--font-body);
  color: var(--ms-text);
  background: var(--ms-bg);
''')}
}}""",
    )
]

# settings
FILES["settings.css"] = [
    (
        ".st",
        f""".st {{
{section_tokens("st", extra='''  --st-mint: #4edea3;
  --st-magenta: #ff00e5;
  --st-max: 700px;
''', layout='''
  max-width: var(--st-max);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 17.6px;
  font-family: var(--font-body);
  overflow: visible;
  position: relative;
  z-index: 1;
  color: var(--st-text);
  background: var(--st-bg);
''')}
}}""",
    )
]

# auth
FILES["auth.css"] = [
    (
        ".auth-page",
        f""".auth-page {{
{section_tokens("auth", bg="#0a0a0c", layout='''
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--auth-bg);
  color: var(--auth-text);
  overflow: hidden;
''')}
}}""",
    )
]

# checkout
FILES["checkout.css"] = [
    (
        ".checkout",
        f""".checkout {{
{section_tokens("checkout", bg="#0a0a0c", layout='''
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(ellipse at 50% -10%, rgba(16, 185, 129, 0.12), transparent 50%),
    var(--checkout-bg);
  color: var(--checkout-text);
  padding: 24px 16px 40px;
''')}
}}""",
    )
]

# status
FILES["status.css"] = [
    (
        ".status-page",
        f""".status-page {{
{section_tokens("status", bg="#0a0a0c", layout='''
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--status-bg);
  color: var(--status-text);
  overflow: hidden;
  font-family: var(--font-body);
''')}
}}""",
    )
]

# contact — prepend tokens if missing; patch success banner
CONTACT_TOKENS = """
.contact-page {
  /* —— Section tokens (edit here only) —— */
  --contact-success-border: color-mix(in srgb, var(--primary) 40%, transparent);
  --contact-success-bg: color-mix(in srgb, var(--primary) 12%, transparent);
  --contact-success-text: var(--primary);
}

"""

# builder — build-page + ab
FILES["builder.css"] = [
    (
        ".build-page",
        f""".build-page {{
{section_tokens("build", bg="#0e1511", layout='''
  min-height: 100vh;
  background:
    radial-gradient(ellipse at 20% -10%, rgba(16, 185, 129, 0.16), transparent 48%),
    radial-gradient(ellipse at 90% 10%, rgba(173, 123, 255, 0.12), transparent 42%),
    var(--build-bg);
  color: var(--build-text);
''')}
}}""",
    ),
    (
        ".ab",
        f""".ab {{
{section_tokens("ab", extra='''  --ab-mint: #4edea3;
  --ab-magenta: #ff00e5;
  --ab-font-display: "Sora", var(--font-display);
  --ab-font-body: Inter, var(--font-body);
  --ab-font-mono: "JetBrains Mono", var(--font-mono);
  --ab-glass: rgba(255, 255, 255, 0.045);
  --ab-border: rgba(255, 255, 255, 0.1);
  --ab-radius: 18px;
''', layout='''
  max-width: 1152px;
  margin: 0 auto;
  font-family: var(--ab-font-body);
  display: flex;
  flex-direction: column;
  gap: 24px;
  color: var(--ab-text);
  background: var(--ab-bg);
''')}
}}""",
    ),
]


def main() -> None:
    for fname, pairs in FILES.items():
        path = CSS / fname
        text = path.read_text(encoding="utf-8")
        if fname in HEADERS:
            text = patch_header(text, HEADERS[fname])
        for selector, block in pairs:
            text = patch_selector_block(text, selector, block)
        path.write_text(text, encoding="utf-8")
        print(f"updated {fname}")

    # contact.css
    path = CSS / "contact.css"
    text = path.read_text(encoding="utf-8")
    text = patch_header(text, HEADERS["contact.css"])
    if "--contact-success-bg" not in text:
        # insert tokens after header
        text = re.sub(
            r"(^/\*[\s\S]*?\*/\s*)",
            r"\1" + CONTACT_TOKENS,
            text,
            count=1,
        )
    text = text.replace(
        """.contact-success {
  margin: 0 0 20px;
  padding: 13.6px 16px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--primary) 40%, transparent);
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: var(--primary);""",
        """.contact-success {
  margin: 0 0 20px;
  padding: 13.6px 16px;
  border-radius: 12px;
  border: 1px solid var(--contact-success-border);
  background: var(--contact-success-bg);
  color: var(--contact-success-text);""",
    )
    path.write_text(text, encoding="utf-8")
    print("updated contact.css")


if __name__ == "__main__":
    main()

/**
 * Tailwind theme — maps Stitch utility names to CSS variables in base.css.
 * No hex colors here; tokens live in static/css/base.css.
 * Load this script BEFORE the Tailwind CDN script.
 */
window.tailwind = window.tailwind || {};
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        surface: "var(--surface)",
        "surface-dim": "var(--surface-dim)",
        "surface-bright": "var(--surface-bright)",
        "surface-container-lowest": "var(--surface-container-lowest)",
        "surface-container-low": "var(--surface-container-low)",
        "surface-container": "var(--surface-container)",
        "surface-container-high": "var(--surface-container-high)",
        "surface-container-highest": "var(--surface-container-highest)",
        "surface-variant": "var(--surface-variant)",
        "deep-obsidian": "var(--deep-obsidian)",
        "surface-navy": "var(--surface-navy)",
        "on-surface": "var(--on-surface)",
        "on-background": "var(--on-background)",
        "on-surface-variant": "var(--on-surface-variant)",
        outline: "var(--outline)",
        "outline-variant": "var(--outline-variant)",
        primary: "var(--primary)",
        "on-primary": "var(--on-primary)",
        "primary-container": "var(--primary-container)",
        "on-primary-container": "var(--on-primary-container)",
        "primary-fixed": "var(--primary-fixed)",
        "surface-tint": "var(--surface-tint)",
        secondary: "var(--secondary)",
        "secondary-container": "var(--secondary-container)",
        "on-secondary-container": "var(--on-secondary-container)",
        "vibrant-purple": "var(--vibrant-purple)",
        "accent-pink": "var(--accent-pink)",
        "electric-blue": "var(--electric-blue)",
        tertiary: "var(--tertiary)",
        "tertiary-container": "var(--tertiary-container)",
        error: "var(--error)",
        "on-error": "var(--on-error)",
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        full: "9999px",
      },
      spacing: {
        "stack-xs": "0.25rem",
        "stack-sm": "1rem",
        "stack-md": "2.5rem",
        "stack-lg": "5rem",
        gutter: "1.5rem",
        "container-max": "1320px",
      },
      maxWidth: {
        "container-max": "1320px",
      },
      fontFamily: {
        "body-md": ["Inter", "system-ui", "sans-serif"],
        "body-lg": ["Inter", "system-ui", "sans-serif"],
        "label-caps": ["JetBrains Mono", "ui-monospace", "monospace"],
        "headline-lg": ["Plus Jakarta Sans", "system-ui", "sans-serif"],
        "headline-lg-mobile": ["Plus Jakarta Sans", "system-ui", "sans-serif"],
        "headline-md": ["Plus Jakarta Sans", "system-ui", "sans-serif"],
        "display-hero": ["Plus Jakarta Sans", "system-ui", "sans-serif"],
        "display-hero-mobile": ["Plus Jakarta Sans", "system-ui", "sans-serif"],
      },
      fontSize: {
        "body-md": ["16px", { lineHeight: "1.5", fontWeight: "400" }],
        "body-lg": ["18px", { lineHeight: "1.6", fontWeight: "400" }],
        "label-caps": [
          "12px",
          { lineHeight: "1", letterSpacing: "0.1em", fontWeight: "600" },
        ],
        "headline-lg": [
          "40px",
          { lineHeight: "1.2", letterSpacing: "-0.02em", fontWeight: "700" },
        ],
        "headline-lg-mobile": ["32px", { lineHeight: "1.2", fontWeight: "700" }],
        "display-hero": [
          "72px",
          { lineHeight: "1.1", letterSpacing: "-0.04em", fontWeight: "800" },
        ],
        "display-hero-mobile": [
          "48px",
          { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "800" },
        ],
        "headline-md": ["24px", { lineHeight: "1.3", fontWeight: "600" }],
      },
    },
  },
};

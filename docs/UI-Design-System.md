# Zentra — UI Design System (Obsidian)

> Canonical tokens from Google Stitch: **Zentra Obsidian**.  
> Emerald primary · glassmorphic dark · purple/pink accents. Winner Gold is deprecated.

---

```yaml
name: Zentra Obsidian
colors:
  surface: '#0e1511'
  surface-dim: '#0e1511'
  surface-bright: '#343b36'
  surface-container-lowest: '#09100c'
  surface-container-low: '#161d19'
  surface-container: '#1a211d'
  surface-container-high: '#242c27'
  surface-container-highest: '#2f3632'
  on-surface: '#dde4dd'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dde4dd'
  inverse-on-surface: '#2b322d'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#c3c0ff'
  on-secondary: '#1f00a5'
  secondary-container: '#392cc4'
  on-secondary-container: '#b3b0ff'
  tertiary: '#ffb3af'
  on-tertiary: '#650911'
  tertiary-container: '#fc7c78'
  on-tertiary-container: '#711419'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#e3dfff'
  secondary-fixed-dim: '#c3c0ff'
  on-secondary-fixed: '#100069'
  on-secondary-fixed-variant: '#3729c1'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3af'
  on-tertiary-fixed: '#410005'
  on-tertiary-fixed-variant: '#842225'
  background: '#0e1511'
  on-background: '#dde4dd'
  surface-variant: '#2f3632'
  deep-obsidian: '#0a0a0c'
  surface-navy: '#1d1c24'
  vibrant-purple: '#ad7bff'
  electric-blue: '#3b82f6'
  accent-pink: '#ff00e5'
  # Brand narrative alias (gradients / high-impact headers)
  secondary-color: '#6861f2'
typography:
  display-hero:
    fontFamily: Plus Jakarta Sans
    fontSize: 72px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  display-hero-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  stack-xs: 0.25rem
  stack-sm: 1rem
  stack-md: 2.5rem
  stack-lg: 3.75rem   # 60px mobile; 80px tablet (≥768); 100px desktop (≥1024)
  container-max: 1320px
  gutter: 1.5rem
```

---

## Brand & Style

The design system embodies a **Dynamic Tech-Forward** personality, blending the high-energy urgency of e-commerce with the polished, premium feel of high-end SaaS. It is designed to evoke confidence and momentum, signaling to users that they are working with cutting-edge AI technology.

The aesthetic follows a **Glassmorphic & High-Contrast** movement. It utilizes deep, "Obsidian" backgrounds to provide a canvas for vibrant, neon-tinted accents and high-gloss translucent surfaces. The layout is layered and energetic, using Z-axis depth (stacking) and glowing gradients to guide the eye toward primary actions. The tone is authoritative yet futuristic, emphasizing speed, automation, and premium quality.

**Key characteristics:**
- Dark Obsidian canvas; glass cards with blur and light-catch borders.
- Primary conversion color: emerald (`primary-container` `#10b981` / `primary` `#4edea3`).
- Purple / secondary-color gradients for high-impact headers and promo chrome — not for primary CTAs.
- Accent pink only for urgency badges (`NEW`, `Limited Offer`).
- Plus Jakarta Sans display, Inter body, JetBrains Mono labels.
- Pill primary buttons; scale hover (~102–105%).

---

## Colors

The palette is rooted in a **Dark Mode** foundation to maximize the "pop" of high-saturation accents.

### Brand & action

| Token | Hex | Role |
|---|---|---|
| **Primary** | `#4edea3` | Brand mint — links, icons, highlights, italic hero accents |
| **Primary Container** | `#10b981` | Solid primary CTA fill (core conversion) |
| **On Primary** | `#003824` | Text/icons on solid emerald |
| **On Primary Container** | `#00422b` | Text on primary-container (nav CTA) |
| **Surface Tint** | `#4edea3` | Tint / elevation hint |

### Surfaces

| Token | Hex | Role |
|---|---|---|
| **Background / Surface / Surface Dim** | `#0e1511` | Page canvas |
| **Deep Obsidian** | `#0a0a0c` | Footer, dense bands, input fields |
| **Surface Navy** | `#1d1c24` | Nav / glass base (often 60–90% opacity + blur) |
| **Surface Container Lowest** | `#09100c` | Deepest inset |
| **Surface Container Low** | `#161d19` | Alternating section tint |
| **Surface Container** | `#1a211d` | Mid panels |
| **Surface Container High** | `#242c27` | Higher panels |
| **Surface Container Highest / Surface Variant** | `#2f3632` | Chips, elevated edges |
| **Surface Bright** | `#343b36` | Brightest dark surface |

### Text & outline

| Token | Hex | Role |
|---|---|---|
| **On Surface / On Background** | `#dde4dd` | Primary text |
| **On Surface Variant** | `#bbcabf` | Secondary / muted body |
| **Outline** | `#86948a` | Soft outlines |
| **Outline Variant** | `#3c4a42` | Borders, secondary button edges |

### Accents & functional

| Token | Hex | Role |
|---|---|---|
| **Secondary** | `#c3c0ff` | Soft lavender secondary |
| **Secondary Container** | `#392cc4` | Secondary filled surfaces |
| **Secondary Color** (narrative) | `#6861f2` | Gradient start for high-impact headers / banners |
| **Vibrant Purple** | `#ad7bff` | Gradient end, AI flair, feature accents |
| **Accent Pink** | `#ff00e5` | Urgency badges only (`NEW`, `Limited Offer`) |
| **Electric Blue** | `#3b82f6` | Informational highlights (sparingly) |
| **Tertiary / Tertiary Container** | `#ffb3af` / `#fc7c78` | Soft coral tertiary (rare) |
| **Error** | `#ffb4ab` | Errors / “without” cancel states |

### Gradients & glows

- **Impact gradient:** linear `#6861f2` → `#ad7bff` for high-impact headers, promotional banners, active path/progress — **not** primary CTA fill.
- **Urgency gradient:** pink → purple (`#ff00e5` → `#ad7bff`) for limited-time / BETA chrome.
- **Glow Primary:** radial `#4edea3` → transparent, ~15% opacity, ~100px blur — behind hero / highlight cards.
- **Glow Purple / Secondary:** radial purple or secondary-color, same treatment — atmosphere only.
- Do **not** use gold/amber as a brand or CTA color.

---

## Typography

Triple-threat type stack:

1. **Plus Jakarta Sans** — headlines: modern, geometric, tight tracking.
2. **Inter** — body: max legibility for instructional copy.
3. **JetBrains Mono** — labels: developer / AI-processing metadata.

| Role | Font | Size | Weight | LH | Tracking |
|---|---|---:|---:|---:|---:|
| Display Hero | Plus Jakarta Sans | 72px (48 mobile) | 800 | 1.1 | -0.04em (−0.02 mobile) |
| Headline LG | Plus Jakarta Sans | 40px (32 mobile) | 700 | 1.2 | -0.02em |
| Headline MD | Plus Jakarta Sans | 24px | 600 | 1.3 | 0 |
| Body LG | Inter | 18px | 400 | 1.6 | 0 |
| Body MD | Inter | 16px | 400 | 1.5 | 0 |
| Label Caps | JetBrains Mono | 12px | 600 | 1 | 0.1em (always uppercase) |

**Emphasis:** italicization and optional gradient text fills on `display-hero` for transformative keywords (e.g. *scaled*, *automatic*, *built in one click*).

---

## Layout & Spacing

**Layered Fluid Grid** — content in distinct stacks with `stack-lg` between major sections.

| Token | Value |
|---|---|
| `stack-xs` | 0.25rem |
| `stack-sm` | 1rem |
| `gutter` | 1.5rem |
| `stack-md` | 2.5rem |
| `stack-lg` | 60px / 80px / 100px (mobile / tablet / desktop) |
| `container-max` | 1320px |

- **Desktop:** 12-column, 1320px max-width.
- **Tablet:** 8-column, ~32px margins.
- **Mobile:** 4-column, ~16px margins.

Decorative glows and gradients may break the grid (absolute positioning). Prefer asymmetrical splits (e.g. 7/5) over rigid equal columns when it keeps the UI dynamic.

---

## Elevation & Depth

Depth via **glassmorphism and glows**, not heavy drop shadows.

1. **Surfaces:** `surface-navy` `#1d1c24` at ~60% opacity + `20px` backdrop-blur.
2. **Borders:** 1px solid; prefer a light-catch gradient border (top-left white ~20% → bottom-right transparent) on glass edges.
3. **Glows:** radial brand colors at ~15% opacity, ~100px blur, sitting **behind** cards / hero.

Optional soft `shadow-2xl` on hero media only.

---

## Shapes

| Token | Value | Role |
|---|---:|---|
| `sm` | 0.25rem | Small controls |
| `DEFAULT` | 0.5rem | Inputs, secondary actions |
| `md` | 0.75rem | Mid controls |
| `lg` | 1rem | Cards / containers |
| `xl` | 1.5rem | Large panels, testimonials |
| `full` | 9999px | Primary CTAs, chips, badges |

Hover: subtle scale-up (~102–105%) on interactive elements.

---

## Components

### Buttons

- **Primary:** Pill, `primary-container` `#10b981`, dark/`on-primary` text. High-gloss / scale on hover.
- **Secondary:** Transparent (or `white/5`) with gradient border (`secondary` / `secondary-color` → `vibrant-purple`), or solid `outline-variant` when gradient borders are impractical.
- **Urgency:** Pink → purple gradient fill for limited-time / BETA only — never the default CTA.

### Cards

- **Glass Card:** `surface-navy` @ 0.6 alpha, 20px blur, 1px light-leak border.
- **Highlight Card:** Same glass + faint radial glow (`secondary-color` or primary) behind the card.

### Inputs

- **Field:** `deep-obsidian` background, 1px `outline-variant` border; focus → primary border + subtle outer glow.
- **Labels:** `label-caps` (JetBrains Mono), ~4px above the field.

### Chips & badges

- High-contrast pills. `accent-pink` for `NEW` / `BETA` / limited offer so they read first.
- Winning / success meta uses primary emerald, not pink.

### Progress & lists

- Checkmarks: primary emerald `#10b981` / `#4edea3`.
- Step / flow lines: `secondary-color` → purple gradient to signify path.

### Nav

- Fixed glass navy bar; brand wordmark in primary; active link primary + underline; Log In text + Get Started primary pill.

---

## Do's and Don'ts

### Do
- Use emerald for every primary conversion CTA and success check.
- Use purple / secondary-color gradients for promo headers, progress paths, and secondary borders.
- Keep pink for urgency badges only.
- Keep glass + blur as the default marketing card language.

### Don't
- Do not use Winner Gold / amber.
- Do not make pink or purple the default primary button fill.
- Do not flatten marketing into solid white sections without intent.
- Do not skip light-catch borders on glass cards when polish matters.

---

## Responsive Behavior

| Breakpoint | Columns | Notes |
|---|---:|---|
| Mobile | 4 | Display hero 48px; stack CTAs; collapse nav |
| Tablet | 8 | 2-col niches / compare |
| Desktop | 12 | Full bento, asymmetrical hero splits OK |

Touch targets ≥ 44px. Primary CTAs remain large (`py-4` class sizing).

---

## Iteration Guide

1. Start on `background` `#0e1511`; alternate with `surface-container-low` bands.
2. One `primary-container` pill for the main action; secondary is outlined / gradient-border.
3. Accent a hero keyword with primary (italic) or rare gradient text fill.
4. Wrap showcases in glass cards; put glows behind, not on, copy.
5. When tempted to add a new CTA hue — don’t. Emerald = action, purple = AI/impact, pink = urgency only.

---

## CSS variable map (implementation)

```css
--background: #0e1511;
--surface: #0e1511;
--deep-obsidian: #0a0a0c;
--surface-navy: #1d1c24;
--surface-container-low: #161d19;
--surface-container: #1a211d;
--surface-container-high: #242c27;
--surface-container-highest: #2f3632;
--primary: #4edea3;
--primary-container: #10b981;
--on-primary: #003824;
--on-primary-container: #00422b;
--secondary: #c3c0ff;
--secondary-color: #6861f2;
--vibrant-purple: #ad7bff;
--accent-pink: #ff00e5;
--electric-blue: #3b82f6;
--on-surface: #dde4dd;
--on-surface-variant: #bbcabf;
--outline: #86948a;
--outline-variant: #3c4a42;
--error: #ffb4ab;
--glass: rgba(29, 28, 36, 0.6);
```

---

## Known Gaps

- In-product wizard/dashboard light theme is not fully specified in Obsidian — keep product surfaces simple until defined.
- True CSS gradient borders on secondary buttons may need a wrapper technique; solid `outline-variant` is an acceptable interim.
- Material Symbols from Stitch HTML are optional; prefer a small SVG set in Next.js.
- Promo countdown / “65% Off” is reference chrome — only ship with real offers.

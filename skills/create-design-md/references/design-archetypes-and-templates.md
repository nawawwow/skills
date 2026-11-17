# Design Archetypes & Production Templates

This guide provides complete blueprints and selection criteria for the **6 curated `DESIGN.md` archetypes** bundled in `generate_design_md.py`, covering both **YAML Front Matter** and **Interleaved YAML** layouts.

---

## 1. Archetype Selection Matrix

```text
┌────────────────────────┬───────────────────────────────────┬────────────────────────────────────┐
│ Archetype Key          │ Target Product Domain             │ Signature Aesthetic Reference      │
├────────────────────────┼───────────────────────────────────┼────────────────────────────────────┤
│ editorial-prestige     │ Publishing, Fintech, Luxury, Docs │ 1970s broadsheet & art monograph   │
│ atmospheric-minimal    │ DevTools, AI IDEs, Command UIs    │ Linear / flight-deck telemetry     │
│ enterprise-clarity     │ B2B SaaS, ERP, Data Dashboards    │ Swiss tabular grid & Stripe clarity│
│ warm-organic           │ Lifestyle, Wellness, Community    │ Botanical apothecary & print zine  │
│ atmospheric-glass      │ Spatial UI, Media, Weather, HUDs  │ Optical glass & depth luminance    │
│ technical-handout      │ RFCs, Research Tools, Specs       │ University CS seminar handout      │
└────────────────────────┴───────────────────────────────────┴────────────────────────────────────┘
```

---

## 2. Mode A: YAML Front Matter Template (`--layout frontmatter`)

Use YAML Front Matter when you want all normative tokens consolidated at the top of `DESIGN.md` for immediate machine parsing (matching official fixtures like `HERITAGE.md` and `examples/atmospheric-glass/DESIGN.md`).

```markdown
---
version: "alpha"
name: "Heritage"
description: "Architectural minimalism and broadsheet editorial gravitas with high-contrast warm neutrals."
colors:
  primary: "#1A1C1E"
  on-primary: "#FFFFFF"
  secondary: "#595F65"
  on-secondary: "#FFFFFF"
  tertiary: "#B8422E"
  on-tertiary: "#FFFFFF"
  neutral: "#F7F5F2"
  surface: "#FFFFFF"
  on-surface: "#1A1C1E"
  outline: "#D4D0C8"
  error: "#BA1A1A"
  on-error: "#FFFFFF"
typography:
  h1:
    fontFamily: "Public Sans"
    fontSize: "48px"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: "Public Sans"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label-caps:
    fontFamily: "Space Grotesk"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.0
    letterSpacing: "0.08em"
rounded:
  sm: "4px"
  md: "8px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.sm}"
    padding: "{spacing.md}"
    height: "44px"
  card-surface:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
---

## Overview

Architectural Minimalism meets Journalistic Gravitas. The interface evokes a
1970s broadsheet monograph or contemporary gallery exhibition.

## Colors

- **Primary (`{colors.primary}`) — Deep Broadsheet Ink**: Headlines and body copy paired with `{colors.on-primary}`.
- **Secondary (`{colors.secondary}`) — Archival Slate**: Captions and metadata paired with `{colors.on-secondary}`.
- **Tertiary (`{colors.tertiary}`) — Boston Clay**: Primary CTA accent paired with `{colors.on-tertiary}`.
- **Neutral (`{colors.neutral}`) & Surface (`{colors.surface}`)**: Warm limestone canvas and gallery card white (`{colors.on-surface}`, `{colors.outline}`).
- **Error (`{colors.error}`)**: Validation alert paired with `{colors.on-error}`.

## Typography

Pairs **Public Sans** (`h1`, `body-md`) with **Space Grotesk** (`label-caps`) for technical numerals.

## Layout

12-column grid (max `1200px`) on an `8px` spatial unit (`{spacing.sm}`, `{spacing.md}`, `{spacing.lg}`).

## Elevation & Depth

Tonal layering between `{colors.neutral}` and `{colors.surface}` using `1px solid` `{colors.outline}` borders.

## Shapes

Architectural sharpness with `{rounded.sm}` (`4px`) controls, `{rounded.md}` (`8px`) cards, and `{rounded.full}` pills.

## Components

- **Buttons (`button-primary`)**: `44px` height, `{colors.tertiary}` fill, `{rounded.sm}` radius.
- **Cards (`card-surface`)**: `{colors.surface}` fill, `{spacing.lg}` padding, `1px` `{colors.outline}` border.

## Do's and Don'ts

- **Do** reserve `{colors.tertiary}` for the single primary action per view.
- **Do** enforce WCAG AA (`>= 4.5:1`) contrast on all component text.
- **Don't** use neon gradients, glowing orbs, or pure `#000000` on `#FFFFFF`.
- **Don't** mix rounded blobs with sharp `4px` controls.
```

---

## 3. Mode B: Interleaved YAML Template (`--layout interleaved`)

Use Interleaved YAML when co-locating each token group directly inside its narrative section makes human review easier:

````markdown
---
version: "alpha"
name: "Daylight Prestige"
description: "Editorial design system with interleaved section tokens."
---

## Overview

A monograph-inspired editorial workspace prioritizing calm typographic hierarchy.

## Colors

```yaml
colors:
  primary: "#1A1C1E"
  on-primary: "#FFFFFF"
  tertiary: "#B8422E"
  on-tertiary: "#FFFFFF"
  neutral: "#F7F5F2"
```

- **Primary (`{colors.primary}`)**: Deep ink paired with `{colors.on-primary}`.
- **Tertiary (`{colors.tertiary}`)**: Boston Clay accent paired with `{colors.on-tertiary}`.
- **Neutral (`{colors.neutral}`)**: Warm limestone background canvas.
````

# DESIGN.md Specification & Schema Reference

This reference documents the official **`DESIGN.md`** format specification (`version: alpha`) developed by **Google Labs / Google Stitch** ([`google-labs-code/design.md`](https://github.com/google-labs-code/design.md), `https://stitch.google.com/docs/design-md/overview`).

---

## 1. Dual-Layer Architecture

A `DESIGN.md` document combines two complementary layers in a single UTF-8 Markdown file at the project root:

1. **Normative YAML Design Tokens**: Machine-readable values for colors, typography scales, corner radii, spacing scales, and component bindings.
2. **Contextual Markdown Prose**: Human-and-agent-readable rationale organized under 8 canonical `##` headings explaining _why_ the tokens exist and _how_ to apply them.

### Token Embedding Modes

Design tokens may be embedded using either of two mechanisms (or a hybrid of both):

- **YAML Front Matter**: Enclosed between `---` lines at line 1 of the file.
- **Interleaved YAML Code Blocks**: Distributed across the document as fenced ` ```yaml ` blocks inside their corresponding `##` sections.

> [!IMPORTANT]
> When multiple YAML blocks exist, all blocks are parsed and merged into a single unified token tree. **Each top-level schema key may be defined at most once across the entire document**; defining the same top-level key in both front matter and a fenced code block (or in two code blocks) is a fatal error (`duplicate-top-key`).

---

## 2. Top-Level YAML Schema Allowlist

The parser recognizes the following top-level keys (max token nesting depth: `20`, max reference depth: `10`):

```yaml
version: "alpha" # Optional spec version string
name: "Heritage" # Design system or brand name
description: "..." # Optional summary of the visual identity
omitted: # Optional list of intentionally omitted sections
  - spacing
  - section: rounded
    reason: "Sharp brutalist corners only; no border radius tokens used"
colors:
  <token-name>: <Color>
typography:
  <token-name>: <Typography>
rounded:
  <scale-level>: <Dimension>
spacing:
  <scale-level>: <Dimension | number>
components:
  <component-name>:
    <property-name>: <string | TokenReference>
```

### Data Types & Formats

| Type             | Valid Formats                                                                                                                                                                     | Examples                                                           |
| :--------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- |
| `Color`          | Hex (`#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`), named CSS colors, `rgb()`, `rgba()`, `hsl()`, `hsla()`, `hwb()`, `oklch()`, `oklab()`, `lch()`, `lab()`, `color-mix(in srgb, ...)` | `"#1A1C1E"`, `"oklch(62% 0.18 250)"`, `"rgba(255, 255, 255, 0.1)"` |
| `Dimension`      | Numeric value with `px`, `em`, or `rem` unit suffix                                                                                                                               | `"48px"`, `"1.5rem"`, `"-0.02em"`                                  |
| `TokenReference` | `{path.to.token}` pointing to a primitive token (or composite `{typography.*}` inside `components`)                                                                               | `"{colors.primary}"`, `"{rounded.md}"`, `"{typography.label-sm}"`  |
| `Typography`     | Object with `fontFamily`, `fontSize`, `fontWeight` (number or string), `lineHeight` (Dimension or unitless multiplier), `letterSpacing`, `fontFeature`, `fontVariation`           | See `typography` examples below                                    |

### Component Sub-Token Properties

Each entry under `components.<component-name>` accepts these standard sub-tokens:

- `backgroundColor`: `<Color | TokenReference>`
- `textColor`: `<Color | TokenReference>`
- `typography`: `<Typography | TokenReference>`
- `rounded`: `<Dimension | TokenReference>`
- `padding`: `<Dimension | TokenReference>`
- `size`: `<Dimension | TokenReference>`
- `height`: `<Dimension | TokenReference>`
- `width`: `<Dimension | TokenReference>`

**Interactive State Variants**: Express states (`hover`, `active`, `pressed`, `disabled`, `focus`) as sibling keys sharing the component prefix (e.g., `button-primary`, `button-primary-hover`, `button-primary-active`).

---

## 3. Canonical Markdown Section Sequence

All structural sections use `##` (`<h2>`) headings. An optional `#` (`<h1>`) title may appear at the top but is ignored by the section parser. Sections may be omitted if unused, but present sections **must** appear in this exact order:

| Order | Canonical Heading      | Accepted Aliases      | Purpose                                                                                                                     |
| :---- | :--------------------- | :-------------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| **1** | `## Overview`          | `## Brand & Style`    | Holistic look-and-feel, specific cultural/architectural reference, target audience, and emotional tone.                     |
| **2** | `## Colors`            | —                     | Semantic roles (`primary`, `secondary`, `tertiary`, `neutral`, `surface`, `error`) paired with descriptive character names. |
| **3** | `## Typography`        | —                     | Font pairings, hierarchy roles (`display`, `headline`, `body`, `label`), weight distribution, and tracking rules.           |
| **4** | `## Layout`            | `## Layout & Spacing` | Grid structure, max container widths, responsive breakpoints, and `8px`/`4px` spacing rhythm.                               |
| **5** | `## Elevation & Depth` | `## Elevation`        | How visual hierarchy is conveyed (tonal layering, hairline borders, or shadow spread/blur/color).                           |
| **6** | `## Shapes`            | —                     | Corner geometry language and `rounded` scale mappings (`none`, `sm`, `md`, `lg`, `xl`, `full`).                             |
| **7** | `## Components`        | —                     | Concrete rules and variants for Buttons, Cards, Inputs, Chips, Lists, Tooltips, Checkboxes, and Radios.                     |
| **8** | `## Do's and Don'ts`   | —                     | Explicit positive and negative guardrails preventing generic styling drift.                                                 |

---

## 4. Consumer Behavior for Unknown Content

Compliant `DESIGN.md` parsers and agents handle unrecognized content deterministically:

| Scenario                                                               | Normative Parser Behavior                                          |
| :--------------------------------------------------------------------- | :----------------------------------------------------------------- |
| Unknown `##` section heading (e.g., `## Iconography`)                  | Preserve without error.                                            |
| Unknown color or typography token key (e.g., `surface-container-high`) | Accept if the value matches a valid Color or Typography structure. |
| Unknown spacing value (e.g., `grid-columns: "12"`)                     | Accept and store as string if not a Dimension.                     |
| Unknown component property (e.g., `borderColor`)                       | Accept with warning.                                               |
| Duplicate `##` section heading (e.g., two `## Colors` sections)        | **Error**; reject the file.                                        |
| Duplicate top-level YAML key across blocks                             | **Error**; reject the file.                                        |

---

## 5. Google Stitch Integration Workflow

1. **Importing into Google Stitch**:
   - Place `DESIGN.md` at the repository root or open your project in Google Stitch (`https://stitch.google.com`).
   - Open **Settings → Design System → Import `DESIGN.md`** and upload or paste the document.
   - Stitch parses the YAML tokens and prose rules so every generated screen adheres to your palette, fonts, radii, and component rules.
2. **Exporting from Google Stitch**:
   - Export an existing Stitch design system via **Settings → Design System → Export `DESIGN.md`**.
   - If the exported file is narrative-only (pure prose without YAML token blocks), run `python skills/create-design-md/scripts/generate_design_md.py . --from-prose stitch-export.md -o DESIGN.md` to upgrade it into a hybrid token+prose specification.

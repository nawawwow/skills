---
name: create-design-md
description: Inspect codebases, extract design tokens, and generate, audit, diff, or export production-grade DESIGN.md files conforming to the Google Stitch and @google/design.md open specification. Use when creating a DESIGN.md from scratch, converting a pure-prose Stitch DESIGN.md into hybrid YAML tokens + prose, extracting tokens from Tailwind v3/v4, CSS variables, or W3C DTCG tokens.json, tailoring visual identity across 6 archetypes (Editorial Prestige, Atmospheric Minimal, Enterprise Clarity, Warm Organic, Atmospheric Glass, Technical Handout), auditing against the 11 @google/design.md linter rules and 12-point quality rubric (WCAG AA contrast, broken token references, orphaned tokens, section order, anti-slop prose), or exporting DESIGN.md tokens to Tailwind v3/v4 and DTCG JSON. Do not use for AGENTS.md coding rules (use create-agents-md) or isolated component coding without DESIGN.md context.
compatibility: Python 3.10+, cross-platform (Windows, macOS, Linux), zero external pip dependencies. Optional @google/design.md CLI (npx -p @google/design.md designmd).
metadata:
  version: "1.0.0"
---

# Create DESIGN.md Process (`create-design-md`)

Engineer, structure, audit, diff, and export machine-and-human-readable **`DESIGN.md`** files that give AI coding agents and design tools (Google Stitch, Google Antigravity, Claude Code, Cursor, GitHub Copilot, v0) a persistent, normative understanding of a product's visual identity and design system.

Introduced by **Google Labs / Google Stitch** ([`google-labs-code/design.md`](https://github.com/google-labs-code/design.md), `https://stitch.google.com/docs/design-md/overview`), `DESIGN.md` is the visual and stylistic counterpart to `README.md` (human onboarding) and `AGENTS.md` (coding agent operational rules). It pairs **normative YAML design tokens** (exact colors, typography scales, radii, spacing, and component bindings) with **contextual Markdown prose** explaining _why_ those choices exist and _how_ agents must apply them.

---

## 1. The 5-Step DESIGN.md Engineering Flow

Follow this standardized workflow whenever creating, migrating, auditing, or exporting a `DESIGN.md` specification:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   5-STEP DESIGN.md ENGINEERING FLOW                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Token Discovery       → Scan Tailwind, CSS vars & DTCG tokens.json  │
│ 2. Archetype & Mode Fit  → Pick archetype & Frontmatter vs Interleaved │
│ 3. Dual-Layer Authoring  → Pair normative YAML tokens + 8 ## sections  │
│ 4. Spec & Quality Audit  → Run 11 lint rules + 12-point rubric (>=80)  │
│ 5. Export & Diff Sync    → Compile to Tailwind v3/v4, DTCG, or Stitch  │
└────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Codebase Token Discovery & Inspection

Run the static token inspector to extract existing CSS custom properties, Tailwind v3/v4 themes, W3C DTCG `tokens.json` files, UI libraries, font stacks, and any existing `DESIGN.md`:

```bash
# Inspect current repository and print human-readable summary
python skills/create-design-md/scripts/inspect_design_tokens.py .

# Output structured discovery metadata as JSON
python skills/create-design-md/scripts/inspect_design_tokens.py . --json
```

### Step 2: Archetype & Token Embedding Alignment

Select the **token embedding layout** and **visual archetype** that best fit the product:

1. **Token Embedding Modes** (both parse into a single unified token tree; never duplicate a top-level YAML key across blocks):
   - **YAML Front Matter (`--layout frontmatter`, default)**: Places `version`, `name`, `description`, `colors`, `typography`, `rounded`, `spacing`, and `components` inside a single `--- ... ---` block at line 1, followed by the 8 `##` prose sections.
   - **Interleaved YAML Code Blocks (`--layout interleaved`)**: Places metadata (`version`, `name`, `description`) in frontmatter and embeds fenced ` ```yaml ` blocks (`colors:`, `typography:`, `spacing:`, `rounded:`, `components:`) directly inside their corresponding `##` sections.
2. **6 Curated Design Archetypes**:
   - `editorial-prestige`: Broadsheet monograph & gallery gravitas (warm limestone canvas, deep ink, single clay accent).
   - `atmospheric-minimal`: Precision dark instrument UI (obsidian canvas, 1px hairline borders, monospace telemetry labels).
   - `enterprise-clarity`: High-legibility B2B SaaS & dense tabular analytics workspace.
   - `warm-organic`: Tactile consumer lifestyle & community warmth (oat-milk surfaces, espresso ink, forest moss accent).
   - `atmospheric-glass`: Multi-layered translucent spatial UI with depth-aware luminance.
   - `technical-handout`: Austere 1970s seminar handout & specification aesthetic with zero ornament.

See: [design-md-spec-and-schema.md](references/design-md-spec-and-schema.md) and [design-archetypes-and-templates.md](references/design-archetypes-and-templates.md).

### Step 3: Dual-Layer Authoring (Normative Tokens + 8 Canonical Sections)

Generate a baseline `DESIGN.md` or convert a pure-prose Google Stitch export:

```bash
# Generate DESIGN.md using YAML frontmatter (default) and auto-detected archetype
python skills/create-design-md/scripts/generate_design_md.py .

# Generate with explicit archetype, brand name, and interleaved YAML blocks
python skills/create-design-md/scripts/generate_design_md.py . --name "Meridian" --archetype atmospheric-minimal --layout interleaved -o DESIGN.md

# Hydrate generated DESIGN.md with hex colors discovered in codebase CSS/Tailwind
python skills/create-design-md/scripts/generate_design_md.py . --hydrate -o DESIGN.md

# Convert a pure-prose Stitch DESIGN.md export into a hybrid token+prose DESIGN.md
python skills/create-design-md/scripts/generate_design_md.py . --from-prose stitch-export.md -o DESIGN.md
```

Enforce the **8 Canonical `##` Sections** in exact order (sections may be omitted if unused, but present sections must follow this sequence):

| #   | Canonical Heading (`##`) | Accepted Aliases      | Associated YAML Key   |
| :-- | :----------------------- | :-------------------- | :-------------------- |
| 1   | `## Overview`            | `## Brand & Style`    | `name`, `description` |
| 2   | `## Colors`              | —                     | `colors`              |
| 3   | `## Typography`          | —                     | `typography`          |
| 4   | `## Layout`              | `## Layout & Spacing` | `spacing`             |
| 5   | `## Elevation & Depth`   | `## Elevation`        | —                     |
| 6   | `## Shapes`              | —                     | `rounded`             |
| 7   | `## Components`          | —                     | `components`          |
| 8   | `## Do's and Don'ts`     | —                     | —                     |

See: [prose-philosophy-and-anti-slop.md](references/prose-philosophy-and-anti-slop.md).

### Step 4: Specification Linting & 12-Point Quality Audit

Validate `DESIGN.md` against all **11 official `@google/design.md` linter rules** and the **12-point (100-score) quality rubric** (enforcing an **80/100 passing gate** and **0 errors**):

```bash
# Run standalone zero-dependency Python linter & 12-point rubric auditor
python skills/create-design-md/scripts/audit_design_md.py DESIGN.md

# Output structured JSON findings
python skills/create-design-md/scripts/audit_design_md.py DESIGN.md --json

# Optional: Run official @google/design.md CLI on Windows PowerShell
# IMPORTANT: Use the dot-free 'designmd' alias with -p so Windows does not open DESIGN.md in a text editor!
npx -p @google/design.md designmd lint DESIGN.md
```

See: [quality-rubric-and-linter-rules.md](references/quality-rubric-and-linter-rules.md).

### Step 5: Token Export, Diffing & Stitch Synchronization

Compile `DESIGN.md` tokens into framework configurations or compare versions for regressions:

```bash
# Export to Tailwind CSS v4 @theme block (CSS custom properties)
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format css-tailwind -o theme.css

# Export to Tailwind CSS v3 theme.extend JSON
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format json-tailwind -o tailwind.theme.json

# Export to W3C Design Tokens Format Module (DTCG tokens.json)
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format dtcg -o tokens.json

# Diff two DESIGN.md versions and fail (exit 1) if errors or warnings regress
python skills/create-design-md/scripts/export_design_md.py DESIGN-v1.md --diff DESIGN.md
```

See: [token-interoperability-and-migration.md](references/token-interoperability-and-migration.md).

---

## 2. Core DESIGN.md Invariants

1. **Specific References Over Generic Adjectives (`PHILOSOPHY.md`)**: Never write generic AI-slop adjectives (_"modern, clean, trustworthy, premium"_). Anchor `## Overview` in a specific cultural, architectural, or print reference (e.g., _"A 1970s graduate computer science seminar handout"_ or _"Broadsheet monograph meets contemporary gallery"_).
2. **Normative Token & Prose Synchronization**: Every color defined in `colors:` must be referenced by at least one component (`{colors.*}`) or prose explanation (`orphaned-tokens` rule), and `primary` must always be defined (`missing-primary` rule).
3. **Strict WCAG 2.2 AA Component Contrast**: Every component defining both `backgroundColor` and `textColor` must achieve at least **4.5:1** contrast ratio (`contrast-ratio` rule).
4. **Canonical Section Sequence**: Never duplicate `##` section headings or top-level YAML keys across blocks, and always maintain the 1–8 canonical section order (`section-order` rule).
5. **Windows PowerShell CLI Invocation**: On Windows, never run `npx @google/design.md` directly because `.md` triggers Windows file association; always invoke `npx -p @google/design.md designmd <command> DESIGN.md` or use the bundled Python scripts.

---

## 3. Bundled Automation Scripts Reference

| Script                             | Purpose                                                                                                                       | Example Usage                                                                                                |
| :--------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| `scripts/inspect_design_tokens.py` | Scans codebase (`package.json`, CSS vars, Tailwind v3/v4, DTCG JSON, existing `DESIGN.md`) and recommends an archetype.       | `python skills/create-design-md/scripts/inspect_design_tokens.py . --json`                                   |
| `scripts/generate_design_md.py`    | Generates a spec-compliant `DESIGN.md` (`frontmatter` or `interleaved`) across 6 archetypes or converts Stitch prose exports. | `python skills/create-design-md/scripts/generate_design_md.py . --archetype editorial-prestige -o DESIGN.md` |
| `scripts/audit_design_md.py`       | Runs all 11 `@google/design.md` lint rules + 12-point quality rubric (0–100 score, `>= 80` gate).                             | `python skills/create-design-md/scripts/audit_design_md.py DESIGN.md`                                        |
| `scripts/export_design_md.py`      | Exports tokens to `css-tailwind`, `json-tailwind`, or `dtcg`, and diffs two `DESIGN.md` files for regressions.                | `python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format css-tailwind`                 |

---

## 4. Deep Reference Guides

Load these references on demand for detailed schemas, templates, and troubleshooting:

- [DESIGN.md Specification & Schema](references/design-md-spec-and-schema.md): Complete `@google/design.md` (`version: alpha`) token schema, allowed keys, `{path.to.token}` resolution rules, and Google Stitch import/export workflow.
- [Design Archetypes & Templates](references/design-archetypes-and-templates.md): Production blueprints for all 6 archetypes in both YAML Front Matter and Interleaved YAML modes.
- [Prose Philosophy & Anti-Slop Craft](references/prose-philosophy-and-anti-slop.md): Applying Google Labs' `PHILOSOPHY.md`—specific cultural references, evocative token naming, and negative constraints.
- [Quality Rubric & Linter Rules](references/quality-rubric-and-linter-rules.md): Detailed breakdown of the 11 official `@google/design.md` linter rules, the 12-point scoring rubric, and Windows CLI tips.
- [Token Interoperability & Migration](references/token-interoperability-and-migration.md): Compiling `DESIGN.md` to Tailwind v3/v4 and W3C DTCG `tokens.json`, diffing versions in CI, and migrating pure-prose Stitch files.

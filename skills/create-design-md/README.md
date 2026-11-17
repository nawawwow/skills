# `create-design-md` Antigravity Agent Skill

> Engineer, structure, audit, diff, and export production-grade `DESIGN.md` files conforming to the **Google Stitch** and **`@google/design.md`** open specification.

---

## Overview

While `README.md` orients human developers and `AGENTS.md` governs coding agent commands and boundaries, **`DESIGN.md`** serves as the persistent **visual identity and design system manifest** for AI coding and design agents (Google Stitch, Google Antigravity, Claude Code, Cursor, GitHub Copilot, and v0).

The `create-design-md` skill provides an end-to-end engineering suite:

1. **Automated Codebase Token Discovery**: Scans CSS custom properties, Tailwind v3/v4 configurations, W3C DTCG `tokens.json`, and `package.json` dependencies (`inspect_design_tokens.py`).
2. **Dual-Mode Token Scaffolding Across 6 Archetypes**: Generates `DESIGN.md` files using either **YAML Front Matter** or **Interleaved YAML Code Blocks** across 6 high-character archetypes (`generate_design_md.py`), and converts pure-prose Stitch exports into hybrid token+prose documents.
3. **11 Official Linter Rules + 12-Point Quality Rubric**: Enforces all 11 `@google/design.md` lint rules (`broken-ref`, `missing-primary`, `contrast-ratio` WCAG AA 4.5:1, `orphaned-tokens`, `missing-typography`, `section-order`, `unknown-key`, `token-like-ignored`, `missing-sections`, `omitted-rules`, `token-summary`) plus an **80/100 quality gate** (`audit_design_md.py`).
4. **Zero-Dependency Token Export & Version Diffing**: Exports `DESIGN.md` tokens directly to **Tailwind v4 CSS (`@theme`)**, **Tailwind v3 JSON (`theme.extend`)**, and **W3C DTCG (`tokens.json`)**, or diffs two `DESIGN.md` files for regressions (`export_design_md.py`).

---

## Directory Structure

```text
create-design-md/
├── SKILL.md                                        # Skill instructions & 5-step engineering workflow
├── README.md                                       # Human documentation & quickstart guide
├── scripts/
│   ├── inspect_design_tokens.py                    # Codebase CSS/Tailwind/DTCG token discovery
│   ├── generate_design_md.py                       # 6-archetype generator & Stitch prose converter
│   ├── audit_design_md.py                          # 11-rule spec linter & 12-point quality auditor
│   └── export_design_md.py                         # Tailwind v3/v4, DTCG exporter & regression differ
├── references/
│   ├── design-md-spec-and-schema.md                # Official @google/design.md schema & Stitch flow
│   ├── design-archetypes-and-templates.md          # 6 production archetypes (Frontmatter & Interleaved)
│   ├── prose-philosophy-and-anti-slop.md           # Specific references, character naming & guardrails
│   ├── quality-rubric-and-linter-rules.md          # 11 lint rules, 12-point rubric & Windows CLI guide
│   └── token-interoperability-and-migration.md     # Tailwind/DTCG compilation & CI regression diffing
└── evals/
    ├── trigger-cases.json                          # 20+ positive & negative trigger test prompts
    ├── output-cases.json                           # 5+ scenario test suites with assertions
    └── evals.json                                  # skill-creator benchmark definitions
```

---

## Quickstart

### 1. Inspect Existing Project Tokens

```bash
python skills/create-design-md/scripts/inspect_design_tokens.py .
```

### 2. Generate a Spec-Compliant `DESIGN.md`

```bash
# Default YAML frontmatter mode
python skills/create-design-md/scripts/generate_design_md.py . --archetype editorial-prestige -o DESIGN.md

# Interleaved YAML code blocks mode
python skills/create-design-md/scripts/generate_design_md.py . --archetype atmospheric-minimal --layout interleaved -o DESIGN.md
```

### 3. Audit Against the 11 Linter Rules & 12-Point Rubric

```bash
python skills/create-design-md/scripts/audit_design_md.py DESIGN.md
```

### 4. Export Tokens or Diff Versions

```bash
# Export Tailwind v4 @theme CSS
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format css-tailwind -o theme.css

# Export W3C DTCG tokens.json
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format dtcg -o tokens.json

# Compare two DESIGN.md files for regressions
python skills/create-design-md/scripts/export_design_md.py DESIGN-old.md --diff DESIGN.md
```

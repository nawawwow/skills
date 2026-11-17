# Token Interoperability, Export & Migration Guide

`DESIGN.md` tokens are designed for seamless round-trip conversion between **Tailwind CSS v3**, **Tailwind CSS v4**, **W3C Design Tokens Format Module (DTCG)**, and **Google Stitch**.

---

## 1. Exporting `DESIGN.md` to Framework Configs

Both the bundled Python exporter (`export_design_md.py`) and the official `@google/design.md` CLI compile `DESIGN.md` tokens into three standard targets:

### Target A: Tailwind CSS v4 (`css-tailwind`)

Generates a `@theme { ... }` block with CSS custom properties (`--color-*`, `--font-*`, `--text-*`, `--leading-*`, `--tracking-*`, `--font-weight-*`, `--radius-*`, `--spacing-*`):

```bash
# Zero-dependency Python exporter
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format css-tailwind -o src/styles/theme.css

# Official npm CLI equivalent (Windows PowerShell safe)
npx -p "@google/design.md" designmd export --format css-tailwind DESIGN.md > src/styles/theme.css
```

Example output:

```css
@theme {
  /* Colors */
  --color-primary: #1a1c1e;
  --color-tertiary: #b8422e;
  --color-neutral: #f7f5f2;

  /* Typography */
  --font-public-sans: "Public Sans", sans-serif;
  --text-h1: 48px;
  --leading-h1: 1.1;
  --tracking-h1: -0.02em;
  --font-weight-h1: 600;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;

  /* Spacing */
  --spacing-sm: 8px;
  --spacing-md: 16px;
}
```

### Target B: Tailwind CSS v3 (`json-tailwind` / `tailwind`)

Generates a `theme.extend` JSON object ready to merge into `tailwind.config.js` or `tailwind.config.ts`:

```bash
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format json-tailwind -o tailwind.theme.json
```

### Target C: W3C DTCG Format (`dtcg`)

Generates a standards-compliant W3C Design Tokens Community Group (`$type`, `$value`) JSON file for Figma Variables, Style Dictionary, or FigCraft import:

```bash
python skills/create-design-md/scripts/export_design_md.py DESIGN.md --format dtcg -o tokens.json
```

---

## 2. Version Diffing & CI Regression Gates

When evolving a design system across pull requests, run a structural token and lint diff between the baseline `DESIGN.md` and the updated file:

```bash
python skills/create-design-md/scripts/export_design_md.py DESIGN.baseline.md --diff DESIGN.md
```

The differ reports:

- `tokens.<category>.added`, `removed`, and `modified` keys across `colors`, `typography`, `rounded`, `spacing`, and `components`.
- `findings.before`, `findings.after`, and `findings.delta` (`errors`, `warnings`).
- `regression: true` (exiting with status code `1`) if either `errors` or `warnings` increased in the updated file.

---

## 3. Migrating Existing Projects & Stitch Prose Exports

### Scenario 1: Bootstrapping `DESIGN.md` from an Existing Codebase

When a repository already defines colors and fonts in CSS variables, Tailwind config, or `tokens.json` but has no `DESIGN.md`:

```bash
# 1. Inspect existing tokens
python skills/create-design-md/scripts/inspect_design_tokens.py .

# 2. Generate DESIGN.md hydrated with discovered colors
python skills/create-design-md/scripts/generate_design_md.py . --hydrate -o DESIGN.md

# 3. Verify 100/100 compliance
python skills/create-design-md/scripts/audit_design_md.py DESIGN.md
```

### Scenario 2: Upgrading a Pure-Prose Google Stitch Export

Early Google Stitch exports or community templates (`awesome-design-md`) often contain narrative headings (`Visual Theme & Atmosphere`, `Color Palette & Roles`, etc.) with inline hex codes but no YAML token layer. Upgrade them into a hybrid spec-compliant `DESIGN.md`:

```bash
python skills/create-design-md/scripts/generate_design_md.py . --from-prose stitch-prose.md --name "BrandName" -o DESIGN.md
python skills/create-design-md/scripts/audit_design_md.py DESIGN.md
```

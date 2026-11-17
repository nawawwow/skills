# Quality Rubric & Official Linter Rules (`@google/design.md`)

This reference details the **11 official `@google/design.md` linter rules**, the **12-point (100-score) quality rubric** enforced by `audit_design_md.py`, and cross-platform CLI execution on Windows PowerShell.

---

## 1. The 11 Official `@google/design.md` Linter Rules

Both `npx -p @google/design.md designmd lint DESIGN.md` and `python skills/create-design-md/scripts/audit_design_md.py DESIGN.md` evaluate these 11 specification rules:

| #   | Rule ID              | Severity    | Verification Logic & Remediation                                                                                                                                                 |
| :-- | :------------------- | :---------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `broken-ref`         | **error**   | Flags any `{path.to.token}` reference that fails to resolve in the merged YAML token tree or exceeds max depth (`10`). Fix the target token path.                                |
| 2   | `missing-primary`    | **warning** | Triggers when `colors` is defined but lacks a `primary` key. Always define `colors.primary`.                                                                                     |
| 3   | `contrast-ratio`     | **warning** | Computes sRGB WCAG 2.x relative luminance contrast for every component defining both `backgroundColor` and `textColor`. Pairs below **4.5:1** trigger a warning.                 |
| 4   | `orphaned-tokens`    | **warning** | Flags color tokens defined under `colors:` that are never referenced (`{colors.<name>}`) in `components:` or prose. Bind or remove unused tokens.                                |
| 5   | `token-summary`      | **info**    | Reports total counts of defined `colors`, `typography`, `rounded`, `spacing`, and `components` tokens.                                                                           |
| 6   | `missing-sections`   | **info**    | Notes optional token groups (`spacing`, `rounded`, `components`) that are absent and not declared in `omitted:`.                                                                 |
| 7   | `missing-typography` | **warning** | Triggers when `colors` are defined but no `typography` tokens exist (unless `typography` is in `omitted:`).                                                                      |
| 8   | `section-order`      | **warning** | Verifies that `##` headings appear in canonical 1–8 order (`Overview` → `Colors` → `Typography` → `Layout` → `Elevation & Depth` → `Shapes` → `Components` → `Do's and Don'ts`). |
| 9   | `unknown-key`        | **warning** | Uses Levenshtein edit distance (`<= 2`) to catch misspelled top-level YAML keys (e.g., `colours:` → `colors:`, `spacings:` → `spacing:`).                                        |
| 10  | `token-like-ignored` | **warning** | Flags unknown top-level YAML keys whose values look like colors, dimensions, or typography definitions that would be silently ignored.                                           |
| 11  | `omitted-rules`      | **info**    | Validates entries in the top-level `omitted:` array (`string` or `{ section, reason }`).                                                                                         |

> [!CAUTION]
> **Hard Rejection Errors**: Duplicate `##` section headings (e.g., two `## Colors` headings) or duplicate top-level YAML keys across front matter and interleaved blocks immediately fail validation with exit code `1`.

---

## 2. The 12-Point Quality Rubric (`audit_design_md.py`)

`audit_design_md.py` scores a `DESIGN.md` file from **0 to 100** and enforces a minimum **80/100 passing gate** with **0 errors**:

| #      | Rubric Criterion                                   | Weight | Passing Requirement                                                                                                   |
| :----- | :------------------------------------------------- | :----: | :-------------------------------------------------------------------------------------------------------------------- |
| **1**  | Valid YAML Token Layer & No Duplicate Keys         | 10 pts | Clean YAML parsing with zero duplicate top-level keys across blocks.                                                  |
| **2**  | Primary & Semantic Color Palette Completeness      | 8 pts  | `colors.primary` defined + at least 4 semantic color tokens (`secondary`, `tertiary`, `neutral`, `surface`, `error`). |
| **3**  | Typography Scale & Hierarchy Completeness          | 8 pts  | At least 3 distinct typography levels (`h1`, `body-md`, `label-*`) with `fontFamily` and `fontSize`.                  |
| **4**  | Spacing & Shape (`rounded`) Scales Defined         | 8 pts  | Both `spacing` and `rounded` token maps populated with valid `px`/`rem`/`em` dimensions.                              |
| **5**  | Component Token Bindings & Variants                | 8 pts  | At least 3 components (`button-primary`, `card-surface`, `input-field`, etc.) bound to system tokens.                 |
| **6**  | Zero Broken Token References (`{path.to.token}`)   | 10 pts | 100% of `{...}` references resolve cleanly (`broken-ref == 0`).                                                       |
| **7**  | WCAG AA Component Contrast Compliance (`>= 4.5:1`) | 10 pts | Every component `backgroundColor` + `textColor` pair meets or exceeds `4.5:1` contrast.                               |
| **8**  | Canonical 8-Section Prose Structure & Order        | 8 pts  | All 8 canonical `##` sections present in exact sequence (`1..8`).                                                     |
| **9**  | Specific Reference Prose & Anti-Slop Discipline    | 10 pts | Evocative reference-based prose free of generic AI-slop clichés (_"modern, clean"_).                                  |
| **10** | Explicit Negative Constraints (`Do's and Don'ts`)  | 8 pts  | At least 2 explicit **Do** rules and 2 explicit **Don't** guardrails in `## Do's and Don'ts`.                         |
| **11** | Token-to-Prose & Component Synchronization         | 6 pts  | Zero orphaned color tokens (`orphaned-tokens == 0`).                                                                  |
| **12** | Zero Unreplaced Placeholder Tokens                 | 6 pts  | No `[TODO]`, `FIXME`, `<your-...>`, or `REPLACE_WITH_` strings.                                                       |

---

## 3. Running `@google/design.md` on Windows PowerShell

On Windows, the `.md` extension in the binary name `design.md` collides with the Windows shell file association for Markdown files (causing `npx @google/design.md` to open an editor or return no output). Always invoke the dot-free **`designmd`** binary alias via `npx -p`:

```powershell
# Lint DESIGN.md with the official npm package on Windows PowerShell
npx -p "@google/design.md" designmd lint DESIGN.md

# Diff two versions of DESIGN.md
npx -p "@google/design.md" designmd diff DESIGN-old.md DESIGN.md

# Print the official specification and active lint rules
npx -p "@google/design.md" designmd spec --rules
```

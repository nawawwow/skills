# Prose Philosophy & Anti-Slop Craft for DESIGN.md

This guide codifies the authoring principles from Google Labs' official `PHILOSOPHY.md` (`google-labs-code/design.md`) and anti-slop UI engineering standards.

---

## 1. Core Axiom: Prose Carries the Design

> _"The quality of a generated design is determined less by the precision of its values than by how clearly the intent is described. Prose, not Tokens, is the focus of the specification."_ — `PHILOSOPHY.md`

Tokens provide exact values (`#1A1C1E`, `16px`), but without rich prose explaining **role, proportion, and restraint**, an AI agent can still assemble those exact hex codes into a generic SaaS template.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                 GENERIC ADJECTIVES vs. SPECIFIC REFERENCE              │
├────────────────────────────────────────────────────────────────────────┤
│ ❌ WEAK (Region):  "A modern, clean, trustworthy, premium SaaS UI."    │
│    → Evokes nothing specific; agent defaults to generic training slop. │
│                                                                        │
│ ✅ STRONG (Point): "A 1970s graduate computer science seminar handout  │
│    printed on warmed xerox stock with a single vermilion diagram ink." │
│    → Evokes a complete world: margins, rules, typography, and limits.  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Pairing Character Names with System Tokens

In `## Colors`, always pair three elements for every palette entry:

1. **System Token Reference**: `{colors.tertiary}` (so the agent binds the exact token).
2. **Evocative Character Name**: _"Boston Clay"_, _"Warm Limestone"_, _"Deep Broadsheet Ink"_, or _"Obsidian Canvas"_.
3. **Strict Functional Scope & Exclusion**: Where the color **must** be used and where it **must never** appear.

### Example

```markdown
- **Paper (`{colors.neutral}`) — Warmed Xerox Stock**: Serves as the universal page canvas; never pure `#FFFFFF` white.
- **Ink (`{colors.primary}`) — Graphite Warm**: Carries all body copy, headlines, and table rules; never pure `#000000` black.
- **Vermilion (`{colors.tertiary}`) — Diagram Annotation Red**: Appears exclusively inside chart callouts and primary CTAs—never on headings, page numerals, or navigation chrome.
```

---

## 3. Writing High-Signal Negative Constraints (`## Do's and Don'ts`)

AI coding agents exhibit strong priors toward training-set clichés (purple-to-blue gradients, glowing neon blurs, Inter font everywhere, 3-column symmetrical feature cards, and hardcoded Tailwind grays). Your `## Do's and Don'ts` section must explicitly forbid those failure modes:

- **Color Restraint**:
  - **Do** restrict `{colors.tertiary}` to at most one primary interactive element per viewport.
  - **Don't** introduce unapproved inline hex colors, decorative neon glow orbs, or multi-stop background gradients.
- **Typographic Discipline**:
  - **Do** enforce `tabular-nums` (`font-variant-numeric: tabular-nums`) on all numeric columns, counters, and timestamps.
  - **Don't** use more than two font families or exceed three font weights (`400`, `500`, `600`) in a single view.
- **Spatial & Shape Integrity**:
  - **Do** maintain a minimum `44px × 44px` touch target on all interactive controls (`button-primary`, `input-field`).
  - **Don't** mix sharp architectural corners (`{rounded.sm}`) with bubbly `24px` containers in the same interface.

---
name: ui-ux-design
description: Architect, refine, or audit digital product user interfaces and user experiences end-to-end. Use when designing wireframes, responsive layouts, 8-state component lifecycle specifications, design systems, semantic tokens (Tailwind / CSS variables), Nielsen's 10 usability heuristic audits, accessibility reviews (WCAG 2.2 Level AA), touch ergonomics (Fitts's Law, 44px tap targets), anti-slop guidelines and emotional design (Norman's 3 levels, human warmth, editorial typography), or modern Agent UX (Human-AI Interaction) patterns. Make sure to use this skill whenever the user mentions UI, UX, wireframes, user flow, component states, accessibility, contrast ratios, design systems, anti-slop, humanizing UI, or agent interfaces, even if they don't explicitly say "UI/UX design". Do not use for high-level brand strategy or logo design (use branding-process instead), or isolated backend-only code.
compatibility: Python 3.10+, standard file inspection and code editing.
metadata:
  version: "1.1.0"
---

# UI/UX Design & Human-Centered Interface Engineering

Build intuitive, accessible, and code-ready user interfaces and user experiences grounded in cognitive psychology, ergonomic laws, design systems, and inclusive standards.

A digital product succeeds not through aesthetic ornamentation, but through structural clarity, predictable mental models, seamless interactive feedback, and respect for human cognitive limitations.

---

## 1. The 7-Step UI/UX Engineering Flow

Follow this sequence when architecting a new feature, screen layout, or auditing existing interfaces:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     THE 7-STEP UI/UX ENGINEERING FLOW                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Context & Mental Model Discovery → Map persona, JTBD, & intent      │
│ 2. Information Architecture & Layout→ 8pt grid, scanning paths, ASCII  │
│ 3. Cognitive Ergonomics & UX Laws   → Fitts, Hick, Miller, Jakob       │
│ 4. Component State Machine Modeling → Complete 8-state lifecycle       │
│ 5. Accessibility & Inclusive Design → WCAG 2.2 AA, contrast, ARIA      │
│ 6. Anti-Slop Craft & Emotional UX   → Norman's 3 levels, human warmth  │
│ 7. Agent UX & Human-AI Orchestration→ Progressive disclosure, rollback │
└────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Context & Mental Model Discovery

1. **Clarify Intent & Primary Job-to-be-Done (JTBD)**:
   - Identify the user's immediate emotional and practical goal (e.g., _"Quickly approve pending orders without reviewing irrelevant line-item details"_).
2. **Align with Existing Mental Models (Jakob's Law)**:
   - Evaluate what platforms the target user uses daily. Preserve universal conventions for search bars, breadcrumbs, shopping carts, filters, and profile controls.
   - Spend innovation budget strictly on core domain capabilities, never on standard navigation or generic forms.

### Step 2: Information Architecture & Layout Hierarchy

1. **Visual Scanning Paths**:
   - For content-heavy and documentation views: Design for the **F-Pattern** with high-contrast, front-loaded section titles.
   - For landing pages and clean dashboards: Design for the **Z-Pattern** anchoring conversion actions at top-right and bottom-right nodes.
2. **The 8pt Spacing Grid**:
   - Align all margins, paddings, and component heights to multiples of $8\text{ px}$ (with $4\text{ px}$ subgrid for compact icon/badge spacing).
   - Ensure internal component padding is always smaller than the external margin between sibling components.
3. **Structured Text / ASCII Wireframes**:
   - Model layouts across Desktop ($1280\text{ px}$, 12-column) and Mobile ($375\text{ px}$, 1-column) before writing UI code.

_Deep dive_: [information-architecture-and-layout.md](references/information-architecture-and-layout.md).

### Step 3: Cognitive Ergonomics & UX Laws

1. **Motor Execution (Fitts's Law)**:
   - Enforce minimum touch target bounds: **$44 \times 44\text{ px}$** for mobile touch interfaces; **$24 \times 24\text{ px}$** for desktop pointer targets with surrounding clearance.
   - **Secondary & Footer Links**: Never leave footer navigation links, legal links, or social media icons as unpadded $16\text{ px}$ text lines or tiny $< 36\text{ px}$ icons; enforce vertical touch clearance (`py-2` / `min-h-[44px]`) to prevent mobile misclicks.
   - Place high-frequency actions within the bottom-third thumb zone on mobile screens.
2. **Decision Velocity (Hick's Law)**:
   - Reduce visual noise. Break multi-step forms ($> 5$ inputs) into stepped wizards or progressive disclosure sections.
3. **Memory Limits (Miller's Law)**:
   - Chunk complex datasets into bounded clusters of $4 - 6$ items (e.g., phone numbers, card grids, dashboard KPI rows).
4. **Latency & Feedback (Doherty Threshold)**:
   - Provide visual feedback in $< 100\text{ ms}$ on user input (active pressed states, hover highlights).
   - For operations $> 100\text{ ms}$, supply layout-matching skeleton screens rather than blank pages or full-screen spinners.

_Deep dive_: [ux-laws-and-cognitive-heuristics.md](references/ux-laws-and-cognitive-heuristics.md).

### Step 4: Component State Machine Modeling

Treat every interactive element as a finite state machine. Never deliver a design specification that only covers the default resting state.

1. **The 8 Core States**:
   - **Default (Idle)**: Clean resting baseline.
   - **Hover**: Subtle $5\% - 10\%$ lightness shift and elevation affordance.
   - **Active (Pressed)**: Instant mechanical depression ($98\%$ scale or inner shadow).
   - **Focus-Visible**: High-contrast $2\text{ px}$ outline with $2\text{ px}$ offset displayed strictly during keyboard Tab navigation.
   - **Disabled**: Lowered opacity ($40\% - 50\%$) with `aria-disabled="true"` and an explanatory tooltip clarifying _why_ the action is locked.
   - **Loading / Skeleton**: Dimension-locked spinner or shimmering skeleton placeholder preventing duplicate click submissions.
   - **Empty State**: Zero-record view featuring a friendly illustration, explanatory copy, and a primary action button.
   - **Error State**: High-contrast red/amber border, error icon, and inline guidance with actionable recovery steps.

_Deep dive_: [component-states-and-design-systems.md](references/component-states-and-design-systems.md).

### Step 5: Accessibility & Inclusive Design (WCAG 2.2 Level AA)

1. **Contrast Ratios**:
   - Body Text ($< 18\text{ pt}$ / $24\text{ px}$): Minimum **$4.5:1$** against background.
   - Large Text ($\ge 18\text{ pt}$ or $\ge 14\text{ pt}$ bold): Minimum **$3.0:1$**.
   - UI Components & Graphical Icons: Minimum **$3.0:1$**.
   - **Gradient Backgrounds**: For text over CSS gradients, verify contrast against the worst-case color stop (lightest stop for white text; darkest stop for dark text) and pair with a fallback solid `background-color`.
2. **Keyboard Focus & Trapping**:
   - Never apply `outline: none` without a custom high-contrast focus indicator.
   - Trap focus inside active modal dialogs; close and restore focus on `Escape`.
3. **Semantic HTML & Screen Reader Affordances**:
   - Form inputs must be linked to `<label for="id">` or supply `aria-label` (especially on compact single-field inputs like footer newsletter fields or header search bars—`placeholder` is never a valid label substitute).
   - Images must have meaningful `alt` descriptions, or `alt=""` if purely decorative.

_Deep dive_: [accessibility-and-wcag-standards.md](references/accessibility-and-wcag-standards.md).

### Step 6: Anti-Slop Craft & Emotional Design (Human-Centered Resonance)

Reject sterile, repetitive "AI template slop" by applying Don Norman's 3 Levels of Emotional Design:

1. **Visceral (Aesthetic Soul)**:
   - **No Neon Blur Glows**: Ban arbitrary purple/blue blurry radial orbs behind hero text. Use clean whitespace, subtle textures, or real product photography.
   - **Editorial Typography**: Large display titles ($\ge 56\text{ px}$) should utilize balanced medium weights (`font-weight: 500` or `600`) with generous line-height ($1.1 - 1.2$) rather than aggressive yelling bold.
   - **Shape Language**: Employ approachable pill tokens (`rounded-full` / `9999px`) on CTAs and interactive filter chips to invite touch.
2. **Behavioral (Tactile Rhythm & Layout Variety)**:
   - **Break the Bento Monoculture**: Never force every section into a $3 \times 3$ identical card grid. Introduce asymmetric layouts (2/3 anchor + 1/3 rail), full-bleed callout statements, and horizontal rails.
   - **Replace the "Icon-in-a-Box" Trap**: Illustrate features with real UI artifacts, interactive controls, code snippets, or actual screenshots rather than isolated 24px Lucide icons in pastel boxes.
3. **Reflective (Authentic Grounding & Copywriting)**:
   - **Ban Banned Buzzwords**: Strictly purge marketing word salads (*"supercharge", "seamless", "next-gen", "cutting-edge", "empower", "revolutionize"*). Use the **Noun-Action-Outcome** formula.
   - **Grounded Social Proof**: Anchor testimonials and case studies with real human photos, verifiable names, locations, and concrete quantitative outcomes.

_Deep dive_: [anti-slop-and-emotional-design.md](references/anti-slop-and-emotional-design.md).

### Step 7: Agent UX & Human-AI Orchestration

For generative AI and autonomous agent interfaces, follow the 5 AUX Heuristics:

1. **Visibility of Intent**: Display live status badges (`[Thinking...]`, `[Calling Tool: DB]`, `[Awaiting Approval]`).
2. **Progressive Transparency**: Show a one-sentence summary by default, with collapsible reasoning traces and tool outputs.
3. **Confidence Grounding**: Display certainty badges and interactive citation links for AI-generated assertions.
4. **Calibrated Permission Tiers**:
   - _Tier 1 (Autonomous)_: Read-only operations, queries, and summaries run silently.
   - _Tier 2 (Soft Approval)_: Non-destructive drafts execute with an Undo toast ($10\text{s}$ window).
   - _Tier 3 (Hard Checkpoint)_: High-stakes mutations (file deletes, deployments, financial transactions) pause for explicit modal approval.
5. **Guaranteed Reversal**: Present side-by-side diff previews before execution, accompanied by 1-click rollback affordances.

_Deep dive_: [agent-ux-and-human-ai-interaction.md](references/agent-ux-and-human-ai-interaction.md).

---

## 2. Core Operational Invariants

Every agent or engineer utilizing this skill must uphold six non-negotiable invariants:

|   #   | Invariant                              | Rule                                                                                                                          | Violation Consequence                                                               |
| :---: | :------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| **1** | **The 8-State Completeness Invariant** | Every interactive component must define Default, Hover, Active, Focus, Disabled, Loading, Empty, and Error states.            | Missing loading or error states leads to frozen UIs and untracked network failures. |
| **2** | **The Explicit Focus Invariant**       | Keyboard focus indicators (`:focus-visible`) must never be suppressed without an accessible high-contrast replacement.        | Keyboard-only and motor-impaired users lose their cursor position entirely.         |
| **3** | **The Touch Target Invariant**         | Mobile touch targets must measure at least $44 \times 44\text{ px}$; desktop click targets at least $24 \times 24\text{ px}$. | High misclick rates, motor frustration, and WCAG 2.5.8 legal non-compliance.        |
| **4** | **The Contrast Invariant**             | Body text must maintain $\ge 4.5:1$ contrast; UI components and large text $\ge 3.0:1$.                                       | Text is unreadable in bright environments or for visually impaired users.           |
| **5** | **The Anti-Slop Invariant**            | Interfaces must reject cliché AI slop (neon blur orbs, identical bento monocultures, buzzword soup, and ghost avatars).       | Users perceive the product as an untrustworthy, generic, low-effort AI template.    |
| **6** | **The Reversibility Invariant**        | Destructive or AI-automated actions must provide confirmation gates, diff previews, or 1-click Undo affordances.              | Accidental data loss and catastrophic user erosion of trust.                        |

---

## 3. Standalone Python CLI Tooling

This skill bundles zero-dependency Python 3.10+ CLI tools in `scripts/`:

### 1. `audit_ui_ux.py` (Linter & Rubric Scorer)

Audits UI files (HTML, JSX, TSX, CSS, Markdown specs) against the **100-Point UI/UX Quality Rubric** (WCAG contrast, touch targets, state completeness, and Nielsen heuristics):

```bash
# Audit a single UI component or page template
python skills/ui-ux-design/scripts/audit_ui_ux.py --file src/components/Dashboard.tsx

# Audit with strict CI/CD gate (fails if score < 85 or critical issues exist)
python skills/ui-ux-design/scripts/audit_ui_ux.py --file index.html --strict

# Calculate WCAG 2.2 contrast ratio between two hex colors
python skills/ui-ux-design/scripts/audit_ui_ux.py --contrast "#2563eb" "#ffffff"
```

### 2. `generate_component_spec.py` (Specification Scaffolder)

Scaffolds a complete 8-state component specification with Tailwind CSS classes, keyboard navigation mappings, and ARIA attributes:

```bash
# Scaffold an accessible button specification
python skills/ui-ux-design/scripts/generate_component_spec.py --name PrimaryButton --type button --output specs/PrimaryButton.md

# Scaffold an interactive Agent UX task card
python skills/ui-ux-design/scripts/generate_component_spec.py --name AgentTaskCard --type agent-card --format markdown
```

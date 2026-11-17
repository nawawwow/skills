---
name: figcraft-workflows
description: Orchestrate end-to-end interface design, design systems, prototyping, Dev Mode handoff, workshop boards, and batch asset automation in FigCraft via its MCP server and figcraft-cli. Use when creating or editing .figcraft, .fig, .sketch, or .penpot files, building auto-layout screens (horizontal, vertical, wrap, grid), authoring components, variants, and slots, configuring styles and multi-mode variables (Light/Dark, JSON/CSS/Tailwind v4/Flutter export), drawing or boolean-merging vectors, wiring interactive prototypes with conditional logic, generating Dev Mode code (CSS, HTML, React, Vue, Tailwind, Leptos, SwiftUI, Compose, ArkUI, Flutter) or Code Connect links, resolving comment threads with wait_for_changes, managing design branches, facilitating whiteboard workshops (stickies, connectors, timers, voting), or running batch data.fill exports. Make sure to use this skill whenever the user mentions FigCraft, .figcraft files, or calls figcraft MCP tools.
compatibility: FigCraft MCP server (18 native tools + 636 engine commands) and/or figcraft-cli.
metadata:
  version: "1.0.0"
---

# FigCraft Agentic Workflows & Automation Engineering

Execute deterministic, high-precision interface design, design system engineering, interactive prototyping, developer handoff, and collaborative whiteboarding in **FigCraft** using its Model Context Protocol (MCP) server and `figcraft-cli`.

Every menu item, panel action, and canvas gesture in FigCraft maps to an underlying engine command (636 commands across 30+ namespaces). AI agents operate on the exact same engine whether running headless in the background (`figcraft-cli mcp`) or attached live to a visible user window (`figcraft --control 7979` + `figcraft-cli mcp --attach 7979`).

---

## 1. The 6-Step Agentic FigCraft Execution Loop

Follow this sequence whenever creating, modifying, inspecting, or handing off designs in FigCraft:

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                 THE 6-STEP AGENTIC FIGCRAFT EXECUTION LOOP                 │
├────────────────────────────────────────────────────────────────────────────┤
│ 1. Context & Document Inspection → inspect_document / get_node / templates │
│ 2. Token & Style Foundation      → variable.* (modes) & style.*            │
│ 3. Atomic Hierarchy Construction → batch ($ref / $step) + auto layout      │
│ 4. Component & Prototype Wiring  → component.*, instance.*, proto.*        │
│ 5. Visual & Structural Verification → inspect_document + screenshot        │
│ 6. Handoff, Branching & Export   → inspect.code, comment.*, export, save   │
└────────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Context & Document Inspection

1. **Inspect Before Mutating**:
   - Always call `inspect_document` (or read `figcraft://document`) first to discover the active document `id`, pages, current selection, existing styles, variable count, and layer hierarchy.
   - On large documents where `inspect_document` returns a `truncated` marker, use `inspect_document {outline: true}` or `run_command` with `node.find {name, type, text, component}` to locate target IDs, then call `get_node {id, depth, fields}` on the specific subtree.
2. **Bootstrap from Templates or Presets**:
   - Instead of guessing viewport dimensions, query `run_command {command: "frame.presets"}` (39 presets across Phone, Tablet, Desktop, Presentation, Watch, Paper, Social media) or create a frame directly via `run_command {command: "frame.create", params: {preset: "iPhone 16 Pro", name: "Home"}}`.
   - To start from a complete multi-screen foundation, list starter templates via `run_command {command: "template.list"}` (`mobile-app`, `landing-page`, `dashboard`, `design-system`, `wireframe-kit`, `social-posts`, `slides`, `icon-set`) and instantiate via `run_command {command: "file.newFromTemplate", params: {template: "mobile-app"}}`.

### Step 2: Token & Style Foundation

1. **Multi-Mode Variables (`variable.*`)**:
   - Create collections with modes (e.g., `["Light", "Dark"]`) via `variable.createCollection`, populate tokens (`color`, `number`, `string`, `boolean`, aliases `{alias}`, alpha `{alpha}`, or color mixes `{mix}`) via `variable.create` and `variable.set`, and bind them to layers via `variable.bind` or inline inside `set_properties` using `{"$var": "Brand/Primary"}`.
   - Switch any frame or page between themes using `variable.setMode {ids: [frameId], collection: "Theme", mode: "Dark"}`.
2. **Reusable Styles (`style.*`)**:
   - Define `paint`, `text`, `effect`, or `grid` styles via `style.create` and link variables inside styles with `style.bind` so every layer using the style adapts automatically to its frame's active mode.

_Deep dive_: [components-styles-variables.md](references/components-styles-variables.md).

### Step 3: Atomic Hierarchy Construction (`batch` + Auto Layout)

1. **Prefer `batch` with `$ref` over Sequential Single Calls**:
   - Group related creation and styling steps into a single `batch` call (`onError: "abort"` by default). This executes as **one atomic undo step** and eliminates round-trip latency.
   - Name parent steps with `"as": "card"` and reference their returned `id` in child steps using `{"$ref": "card"}` (or `{"$step": 0}`). Access nested result fields with slash paths like `{"$ref": "dup", "field": "ids/0"}` or `{"$ref": "dup", "field": "map/3"}`.
   - **Schema Note (`set_properties` vs. `node.set`)**: The top-level MCP tool `set_properties` wraps property keys inside `props: {...}`, whereas the engine command `node.set` (used inside `batch` or `run_command`) takes property keys (`fill`, `sizingH`, `layout`, etc.) directly inside `params` alongside `ids`.
2. **Coordinate System & Auto Layout Discipline**:
   - Page units equal pixels at 100% zoom (`x` right, `y` down). `create_node` and `set_properties` take `x`/`y` **relative to the parent frame** (groups do not establish a coordinate origin; `inspect_document` reports both parent-relative `x`/`y` and page-space `absoluteBounds`).
   - Inside an **auto-layout frame** (`layout: "horizontal" | "vertical" | "grid"`), child positions are controlled by layout flow (`gap`, `crossGap`, `padding`, `mainAlign`, `crossAlign`, `wrap`) and child sizing (`sizingH`, `sizingV`: `"fixed" | "hug" | "fill"`, plus `minWidth`/`maxWidth`/`minHeight`/`maxHeight`), unless `absolute: true` is set on the child.

_Deep dive_: [layout-and-nodes.md](references/layout-and-nodes.md).

### Step 4: Component Architecture & Prototype Wiring

1. **Components, Variants, Properties & Slots**:
   - Convert frames/groups into components via `component.create`, combine multiple components into a variant set via `component.combineVariants` (or `component.addVariant`), and expose `boolean`, `text`, `instanceSwap`, `variant`, or `slot` properties via `component.addProperty` and `component.makeSlot`.
   - Instantiate via `instance.create` or `instance.place`, customize via `instance.setProperties`, and populate slots via `instance.slotInsert`.
2. **Interactive Prototypes & Stateful Logic**:
   - Wire interactions with `proto.interaction.add` using triggers (`onClick`, `onHover`, `afterDelay`, `keyPress`, controller buttons), actions (`navigate`, `openOverlay`, `swapOverlay`, `closeOverlay`, `scrollTo`, `changeTo`, `setVariable`, `setVariableMode`, `conditional`), and transitions (`instant`, `dissolve`, `smartAnimate`, `moveIn`, `push`, `slideIn`, with easing or custom spring/bezier).
   - Test expressions without mutating state using `proto.evaluate {expression: "count + 1", id: frameId}`.

_Deep dive_: [prototyping-and-dev-mode.md](references/prototyping-and-dev-mode.md).

### Step 5: Visual & Structural Verification

1. **Dual Verification (JSON + Pixels)**:
   - After every structural mutation, inspect the layer tree with `inspect_document` or `get_node` to confirm exact dimensions, `sizing` modes, `fills`, `overrides`, and `warnings` (such as font weight fallback or skipped non-frame auto-layout keys).
   - Call `screenshot` (page or specific `ids`) to visually inspect alignment, text wrapping, contrast, clipping, and visual hierarchy.
2. **Font & Text Fit Hygiene**:
   - Check missing fonts with `text.missingFonts` (`file.fontReport` lists all document fonts). Download open-source Google/Noto fonts when permitted via `font.download`, or load local font files via `text.loadFont`, then run `text.refit` (or `text.fit` to auto-scale text into fixed boxes).

### Step 6: Handoff, Reactive Comments, Branching & Export

1. **Dev Mode & Code Generation**:
   - Mark completed screens with `set_properties {ids: [frameId], props: {devStatus: "readyForDev"}}`.
   - Generate production code via `inspect.code` (`css`, `html`, `react`, `vue`, `tailwind`, `leptos`, `swiftui`, `compose`, `arkui`, `flutter`), link design components to repository components with `codeConnect.set`, and attach specs via `annotation.add`, `devResource.add`, and `devMode.addMeasurement`.
2. **Reactive Comment Resolution Loop**:
   - Fetch open threads with `run_command {command: "comment.list", params: {filter: "open", page: "all"}}`.
   - Apply fixes to the anchored layers, reply with a concise summary via `comment.reply`, and close the thread via `comment.resolve` (note: replying to a resolved thread reopens it, so always reply _before_ resolving).
   - In live attached sessions, subscribe to new feedback using `wait_for_changes {after: cursor, timeoutMs: 20000}` and pass the returned `cursor` to subsequent calls.
3. **Safe Experimentation in Branches & Batch Exports**:
   - Isolate major redesigns with `branch.create`, inspect diffs/conflicts with `branch.review`, sync upstream changes with `branch.updateFromMain`, and commit back as one undo step with `branch.merge`.
   - Export layers or whole files with `export` / `file.export` (`png`, `jpg`, `webp`, `svg`, `pdf` with print `bleed`/`cmyk`/`cropMarks`, `xml` Android Vector Drawable, `fig`, `penpot`), or generate up to 500 data-driven multi-format variations in one undo step with `data.fill`.

_Deep dives_:

- [collaboration-comments-branches-boards.md](references/collaboration-comments-branches-boards.md)
- [files-export-plugins-cli.md](references/files-export-plugins-cli.md)
- [command-catalog-cheatsheet.md](references/command-catalog-cheatsheet.md)

---

## 2. Core Operational Invariants

Every agent executing FigCraft workflows must uphold these seven non-negotiable invariants:

|   #   | Invariant                                  | Rule                                                                                                                                                                      | Violation Consequence                                                                                     |
| :---: | :----------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------- |
| **1** | **Parent-Relative Coordinate Invariant**   | Pass `x` and `y` to `create_node` / `set_properties` relative to the parent **frame** (groups do not reset origin). Omit `x`/`y` for auto-layout children.                | Layers land off-screen or outside their visual container; auto-layout overrides manual coordinates.       |
| **2** | **Vector Origin Offset Invariant**         | Start SVG `path` or `points` data at `(0,0)`, or reposition with `set_properties {x, y}` after creation, because `create_node` adds the path's own bounding-box offset.   | Vector icons and paths render shifted away from their intended `(x, y)` coordinates.                      |
| **3** | **Atomic Batch Transaction Invariant**     | Group multi-node creations and edits into a single `batch` call using `"as"` and `{"$ref": "name"}` rather than firing dozens of separate tool calls.                     | Pollutes the user's Undo history with fragmented steps and leaves half-built UI on intermediate errors.   |
| **4** | **Reply-Before-Resolve Comment Invariant** | When resolving user feedback, always run `comment.reply` _before_ `comment.resolve {resolved: true}`.                                                                     | Calling `comment.reply` after `comment.resolve` automatically reopens the resolved thread.                |
| **5** | **Dual Verification Invariant**            | Always pair structural verification (`inspect_document` / `get_node`) with visual verification (`screenshot`) before declaring a design task complete.                    | Misses text truncation, overlapping layers, invisible fills, or unintended auto-layout hug/fill collapse. |
| **6** | **Dev Mode Edit-Lock Invariant**           | In GUI/attached sessions, remember that `view.devMode` (`Shift+D`) is read-only for interactive tools; toggle back to Design mode before driving interactive UI edits.    | Interactive commands and canvas gestures are blocked with `"Dev Mode only inspects"`.                     |
| **7** | **Explicit Save & Path Safety Invariant**  | Untitled documents have no disk path; pass an explicit `path` on the first `save_file` call, and respect `--automation-read-root` / `--automation-write-root` boundaries. | Unsaved work remains only in memory/recovery cache or fails sandbox path checks.                          |

---

## 3. Native MCP Tools vs. `run_command` Quick Decision Matrix

Use the dedicated high-level MCP tool when available, and fall back to `run_command` (or `batch`) for the remaining 600+ engine commands:

| Task Category              | Dedicated MCP Tool                                         | Equivalent / Extended Engine Commands (`run_command` / `batch`)                                                                                                                                       |
| :------------------------- | :--------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inspect & Verify**       | `inspect_document`, `get_node`, `inspect_ui`, `screenshot` | `node.get`, `node.find`, `file.fontReport`, `selection.colors`, `measure.distances`, `measure.padding`                                                                                                |
| **Create & Style Layers**  | `create_node`, `set_properties`                            | `frame.create` (with `preset`), `shape.*`, `text.create`, `vector.create`, `image.place`, `fill.*`, `stroke.*`, `effect.*`                                                                            |
| **Atomic Multi-Step**      | `batch` (`$ref`, `$step`, `onError`)                       | `command.batch`                                                                                                                                                                                       |
| **Selection & Transform**  | `select`                                                   | `select.byName`, `select.matching`, `select.same*`, `align.*`, `distribute.*`, `arrange.*`, `transform.*`, `object.batchRename`                                                                       |
| **Auto Layout & Grids**    | `set_properties` (`layout`, `gap`, `padding`, `sizingH/V`) | `layout.add`, `layout.suggest`, `layout.remove`, `layout.removeAll`, `layout.setTrack`, `grid.add`                                                                                                    |
| **Components & Libraries** | `create_node {type: "component"}`                          | `component.*`, `instance.*`, `library.*`, `libraries.*`                                                                                                                                               |
| **Styles & Variables**     | `set_properties` (`fill: {"$var": ...}`)                   | `style.*`, `variable.*` (`createCollection`, `addMode`, `create`, `bind`, `setMode`, `export`, `import`)                                                                                              |
| **Vectors & Booleans**     | `create_node {type: "vector"}`                             | `vector.*`, `vector.edit.*`, `shapeBuilder.regions/merge/remove`, `bool.union/subtract/intersect/exclude/flatten`                                                                                     |
| **Prototyping**            | —                                                          | `proto.interaction.*`, `proto.action.*`, `proto.conditional.*`, `proto.flow.*`, `proto.settings`, `proto.evaluate`, `proto.present`, `proto.preview`                                                  |
| **Dev Mode & Handoff**     | —                                                          | `inspect.code`, `inspect.componentCode`, `component.playground`, `codeConnect.*`, `annotation.*`, `devResource.*`, `devMode.*`, `dev.compare`, `dev.resolveChange`                                    |
| **Comments & Watch Loop**  | `wait_for_changes`                                         | `comment.list`, `comment.add`, `comment.reply`, `comment.react`, `comment.resolve`, `comment.prompt`                                                                                                  |
| **Versions & Branches**    | `undo`, `redo`                                             | `file.saveVersion`, `version.*`, `branch.create`, `branch.list`, `branch.open`, `branch.review`, `branch.updateFromMain`, `branch.merge`, `branch.archive`                                            |
| **Whiteboard / Boards**    | —                                                          | `file.newBoard`, `board.sticky`, `board.nextSticky`, `board.shape`, `board.addConnected`, `board.connector`, `board.ink`, `board.stamp`, `board.table`, `board.template`, `board.timer`, `board.vote` |
| **Files, Export & Data**   | `open_file`, `save_file`, `export`                         | `file.*`, `export.add/update/remove`, `file.exportLayers`, `file.exportFramesPdf`, `data.fill`, `text.fit`                                                                                            |
| **Canvas Gestures & Keys** | `pointer`, `key`, `type_text`                              | `tool.set`, `tool.place`, `text.edit.*`                                                                                                                                                               |

---

## 4. Reference Navigation Guide

Load only the reference file(s) needed for your active task:

1. **[layout-and-nodes.md](references/layout-and-nodes.md)**: Read when creating frames (`frame.presets`), sections, shapes, typography, vector paths (`vector.edit.*`, `shapeBuilder.*`, `bool.*`), auto layout (`horizontal`, `vertical`, `grid`, `sizingH/V`, tracks), constraints, or aligning/renaming layers.
2. **[components-styles-variables.md](references/components-styles-variables.md)**: Read when building reusable components, variant sets, slots, component properties, paint/text/effect/grid styles, multi-mode variable collections (Light/Dark, aliases, alpha/mix calculations, JSON/CSS/Tailwind v4/Dart export), or publishing/consuming libraries.
3. **[prototyping-and-dev-mode.md](references/prototyping-and-dev-mode.md)**: Read when wiring interactive prototypes, stateful variable actions, conditional flows, `smartAnimate` transitions, or performing Dev Mode handoff (`inspect.code` for 10 frameworks, `codeConnect.*`, `component.playground`, annotations, measurements, and `dev.compare`).
4. **[collaboration-comments-branches-boards.md](references/collaboration-comments-branches-boards.md)**: Read when resolving comments (`comment.*` + `wait_for_changes`), managing version history (`version.*`), working with design branches (`branch.*`), hosting/joining live sessions (`collab.*`), or running workshop boards (`board.*`).
5. **[files-export-plugins-cli.md](references/files-export-plugins-cli.md)**: Read when importing/opening external formats (`.fig`, `.sketch`, `.penpot`, `.jam`, SVG, REST JSON, Figma clipboard), configuring multi-format/print/Android XML exports, running `data.fill` batch generation, managing WASM plugins/widgets (`plugin.*`, `widget.*`), or using `figcraft-cli` and `--control` / `--attach`.
6. **[command-catalog-cheatsheet.md](references/command-catalog-cheatsheet.md)**: Read when looking up exact parameter signatures across all 636 engine commands, `batch` (`$ref` / `$step`) syntax, or GUI keyboard shortcuts.

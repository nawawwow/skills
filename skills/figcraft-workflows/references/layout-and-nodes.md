# Layout, Coordinate System, Nodes, Auto Layout & Vectors

Comprehensive agent guide for creating layers, configuring Auto Layout (rows, columns, wrapping rows, CSS-like 2D grids), styling paints/effects/typography, drawing/editing vectors, and aligning or renaming layers in FigCraft.

---

## Table of Contents

1. [Coordinate System & Hierarchy Rules](#1-coordinate-system--hierarchy-rules)
2. [Frames, Presets, Sections & Slices](#2-frames-presets-sections--slices)
3. [Auto Layout (Horizontal, Vertical, Wrap & Grid)](#3-auto-layout-horizontal-vertical-wrap--grid)
4. [Constraints, Layout Grids & Guides](#4-constraints-layout-grids--guides)
5. [Shapes, Fills, Strokes & Effects](#5-shapes-fills-strokes--effects)
6. [Typography, Rich Text Ranges & Font Management](#6-typography-rich-text-ranges--font-management)
7. [Vector Drawing, Point Editing, Boolean Groups & Shape Builder](#7-vector-drawing-point-editing-boolean-groups--shape-builder)
8. [Selection, Batch Rename, Alignment & Arrangement](#8-selection-batch-rename-alignment--arrangement)

---

## 1. Coordinate System & Hierarchy Rules

- **Page Units**: `1 unit = 1 px` at 100% zoom (`x` increases right, `y` increases down).
- **Parent-Relative Coordinates (`x`, `y`)**:
  - `create_node` and `set_properties` interpret `x` and `y` **relative to the parent frame** (or the page when there is no parent frame).
  - **Groups do not establish a local coordinate origin**: a layer inside a group still uses its enclosing frame's (or page's) coordinate space.
  - `inspect_document` and `get_node` return **both** parent-frame-relative `x`, `y` and page-space `absoluteBounds: {x, y, width, height}`.
- **Auto-Layout Children**:
  - When a layer's parent is an auto-layout frame (`layout: "horizontal" | "vertical" | "grid"`), the layout engine calculates `x` and `y` automatically.
  - To float a child above an auto-layout frame (e.g., a notification badge or close button), set `props: {"absolute": true, "x": 320, "y": 16, "constraints": {"horizontal": "max", "vertical": "min"}}`.
- **Vector Origin Rule**:
  - In `create_node {type: "vector", path: "...", x, y}` (or `node.set {path}`), `x` and `y` shift the path's own origin: a path whose bounding box starts at `(30, 0)` placed with `x: 10` ends up with its left edge at `10 + 30 = 40`.
  - Always normalize SVG paths to start at `(0, 0)` or call `set_properties {ids: [vecId], props: {x: 10, y: 20}}` after creation to position the left/top edge directly.

---

## 2. Frames, Presets, Sections & Slices

### Creating Frames from Built-In Device Presets

Use `run_command` with `frame.create` and a `preset` name (if `x`/`y` are omitted, FigCraft automatically places the new frame to the right of existing top-level frames):

```json
{
  "command": "frame.create",
  "params": {
    "preset": "iPhone 16 Pro",
    "name": "01 - Sign In",
    "props": {
      "fill": "#0F172A",
      "layout": "vertical",
      "padding": [64, 24, 40, 24],
      "gap": 20,
      "clip": true
    }
  }
}
```

**Built-in `FRAME_PRESETS` (39 presets)**:
- **Phone**: `iPhone 17` (`402×874`), `iPhone 17 Pro` (`402×874`), `iPhone 17 Pro Max` (`440×956`), `iPhone Air` (`420×912`), `iPhone 16` (`393×852`), `iPhone 16 Pro` (`402×874`), `iPhone 16 Pro Max` (`440×956`), `iPhone 16 Plus` (`430×932`), `iPhone SE` (`320×568`), `Android Compact` (`412×917`), `Android Medium` (`700×840`).
- **Tablet**: `iPad mini 8.3` (`744×1133`), `iPad Pro 11"` (`834×1194`), `iPad Pro 12.9"` (`1024×1366`), `Surface Pro 8` (`1440×960`), `Android Expanded` (`1280×800`).
- **Desktop**: `MacBook Air` (`1280×832`), `MacBook Pro 14"` (`1512×982`), `MacBook Pro 16"` (`1728×1117`), `Desktop` (`1440×1024`), `Wireframe` (`1440×1024`), `TV` (`1280×720`).
- **Presentation**: `Slide 16:9` (`1920×1080`), `Slide 4:3` (`1024×768`).
- **Watch**: `Apple Watch Series 10 42mm` (`187×223`), `Apple Watch 41mm` (`176×215`), `Apple Watch 45mm` (`198×242`).
- **Paper**: `A4` (`595×842`), `A5` (`420×595`), `A6` (`297×420`), `Letter` (`612×792`), `Tabloid` (`792×1224`).
- **Social media**: `Instagram post` (`1080×1350`), `Instagram story` (`1080×1920`), `Facebook post` (`1200×630`), `X post` (`1200×675`), `LinkedIn post` (`1200×1200`), `YouTube thumbnail` (`1280×720`), `Dribbble shot` (`1600×1200`).

Flip portrait and landscape dimensions with `run_command {command: "frame.swapOrientation", params: {ids: [frameId]}}`.

### Sections & Slices

- **Section (`type: "section"`, GUI shortcut `Shift+S`)**: Visually groups top-level frames on the canvas into labeled workflow areas.
  - Wrap existing frames in a section: `run_command {command: "object.wrapInSection", params: {ids: [1, 2, 3], name: "Onboarding Flow"}}`.
  - Collapse/expand section contents: `run_command {command: "section.toggleContents", params: {ids: [secId]}}`.
- **Slice (`type: "slice"`, GUI shortcut `S`)**: Marks an export region on the canvas independent of layer boundaries. Toggle visibility via `run_command {command: "view.slices", params: {on: true}}`.
- **Container Conversions**:
  - `object.convertToGroup`, `object.convertToFrame`, `object.convertToSection`, `object.frameSelection` (`Ctrl+Alt+G`), `object.resizeToFit` (`Ctrl+Alt+Shift+R`).

---

## 3. Auto Layout (Horizontal, Vertical, Wrap & Grid)

Auto Layout arranges a frame's, component's, or instance's children in a row, column, wrapping flex container, or 2D grid.

### Container Auto-Layout Properties (`set_properties` / `create_node.props`)

| Property          | Accepted Values                                                                 | Purpose                                                                                      |
| :---------------- | :------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------- |
| `layout`          | `"horizontal"` \| `"vertical"` \| `"grid"` \| `null`                            | Sets or removes auto-layout mode (`Shift+A` / `layout.add`).                                 |
| `gap`             | `number` (alias `columnGap`)                                                    | Primary axis spacing between children (or column gap in `grid`).                             |
| `crossGap`        | `number` (alias `rowGap`)                                                       | Spacing between wrapped lines (`wrap: true`) or row gap in `grid`.                           |
| `padding`         | `number` \| `[top, right, bottom, left]`                                        | Inner padding (or individual `paddingTop`, `paddingRight`, `paddingBottom`, `paddingLeft`).  |
| `mainAlign`       | `"min"` \| `"center"` \| `"max"` \| `"spaceBetween"` \| `"spaceAround"` \| `"spaceEvenly"` | Distribution along the primary axis.                                                         |
| `crossAlign`      | `"min"` \| `"center"` \| `"max"` \| `"baseline"`                                | Alignment across the counter axis (`"baseline"` aligns first text baselines in rows).        |
| `wrap`            | `boolean`                                                                       | Wraps overflowing items into multiple rows (`horizontal`) or columns (`vertical`).           |
| `contentAlign`    | `"auto"` \| `"spaceBetween"`                                                    | How wrapped lines pack along the cross axis.                                                 |
| `sizingH` / `sizingV` | `"fixed"` \| `"hug"` \| `"fill"`                                            | Horizontal and vertical sizing behavior of the frame or child.                               |
| `minWidth` / `maxWidth` / `minHeight` / `maxHeight` | `number` \| `null`                    | Responsive size clamps (`null` clears the limit).                                            |
| `strokesIncluded` | `boolean`                                                                       | Include inside stroke weight in layout box calculations.                                     |
| `reverseZ`        | `boolean`                                                                       | Canvas stacking order (`true` draws the first child on top, useful for overlapping avatars). |

### 2D Grid Auto Layout Properties (`layout: "grid"`)

- **Container**: `gridColumns`, `gridRows`, `columnTracks`, `rowTracks` (arrays of `120` px, `"1fr"`, `"auto"`, or `{sizing: "fixed"|"hug"|"fill", value}`).
  - Update a single track via `run_command {command: "layout.setTrack", params: {ids: [frameId], axis: "columns", index: 0, sizing: "fixed", value: 240}}`.
- **Grid Children**: `gridColumn`, `gridRow` (0-based cell anchor; `null` = auto-placed), `gridColumnSpan`, `gridRowSpan`, `gridAlignH`, `gridAlignV` (`"min" | "center" | "max" | "auto"`).

### Inferring Auto Layout from Freeform Layers

If layers are already positioned manually, run `run_command {command: "layout.suggest", params: {ids: [frameId]}}` (`Ctrl+Alt+Shift+A`) to infer direction, gaps, and padding automatically. Use `layout.removeAll` to strip auto layout recursively from a subtree.

### Example: Building a Responsive Card in One `batch` Call

```json
{
  "label": "Create Feature Card",
  "commands": [
    {
      "command": "node.create",
      "as": "card",
      "params": {
        "type": "frame",
        "name": "Feature Card",
        "width": 342,
        "props": {
          "layout": "vertical",
          "sizingH": "fixed",
          "sizingV": "hug",
          "padding": 20,
          "gap": 12,
          "fill": "#1E293B",
          "cornerRadius": 16,
          "stroke": "#334155",
          "strokeWeight": 1
        }
      }
    },
    {
      "command": "node.create",
      "params": {
        "type": "text",
        "parent": {"$ref": "card"},
        "name": "Title",
        "text": "Instant Prototypes",
        "props": {
          "sizingH": "fill",
          "fontSize": 18,
          "fontStyle": "Bold",
          "fill": "#F8FAFC"
        }
      }
    },
    {
      "command": "node.create",
      "params": {
        "type": "text",
        "parent": {"$ref": "card"},
        "name": "Body",
        "text": "Wire interactive flows with variables, conditions, and smart animations.",
        "props": {
          "sizingH": "fill",
          "fontSize": 14,
          "lineHeight": "150%",
          "fill": "#94A3B8"
        }
      }
    }
  ]
}
```

---

## 4. Constraints, Layout Grids & Guides

For non-auto-layout frames (or `absolute: true` children inside auto-layout frames):
- **Constraints**: `set_properties {ids: [id], props: {constraints: {horizontal: "min"|"max"|"center"|"stretch"|"scale", vertical: "min"|"max"|"center"|"stretch"|"scale"}}}`.
- **Layout Grids**: Add column, row, or uniform square grids via `run_command {command: "grid.add", params: {ids: [frameId], grid: {kind: "columns", count: 12, gutter: 24, offset: 32}}}`. Toggle display with `view.layoutGrids` (`Shift+G`).
- **Ruler Guides**: `guide.add {vertical: true, offset: 120, frame: frameId}`, `guide.move`, `guide.remove`, `guide.clear`.

---

## 5. Shapes, Fills, Strokes & Effects

### Primitive Layer Types

Create with `create_node` (or `shape.*` via `run_command`):
- `rectangle` (`cornerRadius`: `12` or `[tl, tr, br, bl]`, `cornerSmoothing`: `0..1`)
- `ellipse` (`arcStart`, `arcSweep`, `arcInner` for donut charts and progress rings)
- `polygon` (`pointCount`: `3..60`)
- `star` (`pointCount`, `innerRadius`: `0..1`)
- `line` (`width` = length, `rotation` in degrees)
- `arrow` (`width` = length, `startCap`, `endCap`)

### Paints (Fills & Strokes)

- **Solid Colors**: `"#RRGGBB"`, `"#RRGGBBAA"`, or `{"type": "solid", "color": "#3B82F6", "opacity": 0.8}`. Remove fill/stroke with `fill: "none"` or `object.removeFill` / `object.removeStroke`.
- **Gradients**: `linearGradient`, `radialGradient`, `angularGradient`, `diamondGradient`:
  ```json
  {
    "fills": [
      {
        "type": "linearGradient",
        "stops": [
          {"position": 0, "color": "#6366F1"},
          {"position": 1, "color": "#EC4899"}
        ],
        "from": [0, 0],
        "to": [1, 1]
      }
    ]
  }
  ```
- **Live Pattern Fills**: Tile any existing layer across a shape with `run_command {command: "fill.pattern", params: {ids: [targetId], source: iconNodeId, tile: "grid", scale: 1, spacing: [8, 8]}}`.
- **Stroke Options**: `strokeWeight`, `strokeAlign` (`"inside" | "center" | "outside"`), individual sides `strokeSides: [t, r, b, l]` or `strokeBottomWeight: 1`, `strokeCap` / `startCap` / `endCap` (`"none" | "round" | "square" | "lineArrow" | "triangleArrow" | "reversedTriangle" | "circleFilled" | "diamondFilled"`), `strokeJoin` (`"miter" | "bevel" | "round"`), `dashes: [6, 4]`, `widthProfile` (`"uniform" | "wedge" | "taper" | "eye" | "rounded" | "pinch"`), and `brush` (`"taper" | "ink" | "ribbon" | "bristle" | "dots" | "stars" | "confetti" | "leaves"`).

### Effects

Set via `set_properties {props: {effects: [...]}}` or `effect.add`:
- `dropShadow` / `innerShadow`: `{"type": "dropShadow", "color": "#00000033", "offset": [0, 8], "radius": 24, "spread": 0}`
- `layerBlur` / `backgroundBlur`: `{"type": "backgroundBlur", "radius": 16}`
- `noise`, `texture`, `glass` (refraction, depth, dispersion, frost `radius`, `lightAngle`, `lightIntensity`, `splay`).

---

## 6. Typography, Rich Text Ranges & Font Management

### Text Layer Properties

- **Sizing (`textAutoResize`)**:
  - `"widthAndHeight"`: Hugs content on a single unwrapped line (default when `width` is omitted in `create_node`).
  - `"height"`: Fixed width, wraps text and grows vertically (default when `width` is passed to `create_node` or when `sizingH: "fill"` is set inside a vertical auto-layout container).
  - `"none"` / `"truncate"`: Fixed box (`maxLines` truncates with an ellipsis).
- **Typography Keys**: `characters`, `fontFamily`, `fontStyle`, `fontSize`, `lineHeight` (`"auto"`, px number, or `"150%"`), `letterSpacing` (px or `"2%"`), `textAlign` (`"left" | "center" | "right" | "justified"`), `textAlignVertical`, `textCase` (`"original" | "upper" | "lower" | "title" | "smallCaps"`), `textDecoration` (`"none" | "underline" | "strikethrough"`), `paragraphSpacing`, `paragraphIndent`, `listStyle` (`"none" | "bulleted" | "numbered"`), `wrapStyle` (`"auto" | "balance" | "pretty"`), `leadingTrim` (`"none" | "capHeight"`), OpenType `features` (`{"tnum": true, "liga": false}`), variable font `fontVariations` (`{"wght": 650, "wdth": 90}`).
- **Rich Text Sub-Ranges**: Apply mixed styles within a single text node using `run_command {command: "text.style", params: {id: textId, start: 0, end: 5, fontStyle: "Bold", textFills: ["#3B82F6"], hyperlink: "https://craft.wiki"}}`.
- **Text on a Path**: Attach a text layer to a vector/shape contour via `run_command {command: "text.onPath", params: {text: textId, path: curveId, start: 0.1}}`.
- **Auto-Fit Text to Box**: Shrink or scale text to fit a fixed container without single-word orphans via `run_command {command: "text.fit", params: {ids: [textId], maxLines: 2, orphans: true}}`.

### Font Inspection & Missing Fonts

1. Inspect fonts used in the document: `run_command {command: "file.fontReport"}` and `run_command {command: "text.missingFonts"}`.
2. Query available families, styles, OpenType features, and variable axes: `run_command {command: "text.fonts", params: {family: "Inter", axes: true, features: true}}`.
3. Load a local `.ttf`/`.otf`/`.ttc` file for the session: `run_command {command: "text.loadFont", params: {path: "/abs/path/font.ttf"}}` (automatically runs `text.refit`).
4. Download missing Google/Noto fonts (when enabled by user): `run_command {command: "font.download", params: {family: "Plus Jakarta Sans"}}`.

---

## 7. Vector Drawing, Point Editing, Boolean Groups & Shape Builder

### Creating Vectors

Pass SVG `path` data or a `points` array to `create_node {type: "vector"}` (always start path coordinates at `0,0` or set `x`/`y` afterwards):

```json
{
  "type": "vector",
  "name": "Checkmark",
  "x": 16,
  "y": 16,
  "width": 16,
  "height": 12,
  "path": "M0 6 L5 11 L16 0",
  "props": {
    "stroke": "#10B981",
    "strokeWeight": 2,
    "strokeCap": "round",
    "strokeJoin": "round"
  }
}
```

### Non-Destructive Boolean Groups (`bool.*`)

Combine shapes while keeping operands editable inside the boolean group:
- `bool.union` (`Alt+Shift+U`), `bool.subtract` (`Alt+Shift+S`), `bool.intersect` (`Alt+Shift+I`), `bool.exclude` (`Alt+Shift+E`).
- Convert to a single flat vector path with `bool.flatten` or `vector.flatten` (`Ctrl+E` / `Alt+Shift+F`).

### Interactive Shape Builder (`shapeBuilder.*`, GUI `Shift+M`)

1. Inspect intersecting regions across selected shapes (including outlined strokes):
   `run_command {command: "shapeBuilder.regions", params: {ids: [shapeA, shapeB]}}`
2. Merge or punch out specific region indices:
   - `run_command {command: "shapeBuilder.merge", params: {ids: [shapeA, shapeB], regions: [0, 1]}}`
   - `run_command {command: "shapeBuilder.remove", params: {ids: [shapeA, shapeB], regions: [2]}}`

### Vector Path Operations & Point-Level Editing (`vector.*`)

- **Whole-Path Commands**: `vector.outlineStroke` (`Alt+Cmd+O`), `vector.join` (`Cmd+J`), `vector.smoothJoin` (`Shift+Cmd+J`), `vector.deleteHeal` (`Shift+Delete`), `vector.simplify {ids, tolerance}`, `vector.offset {ids, offset}`, `vector.reverse`, `vector.fillRule {rule: "nonZero" | "evenOdd"}`.
- **Vertex/Segment Editing Session (`vector.edit.*`)**:
  1. `vector.edit.begin {ids: [vecId]}`
  2. `vector.edit.state` (inspect vertices, segments, handles, and closed regions)
  3. Mutate geometry: `vector.edit.moveVertices`, `vector.edit.setHandle`, `vector.edit.mirroring`, `vector.edit.smooth`, `vector.edit.bend`, `vector.edit.addVertex`, `vector.edit.cornerRadius`, `vector.edit.paint` (paint-bucket fill closed regions), `vector.edit.cut`, `vector.edit.erase`, `vector.edit.widthPoint` (variable-width stroke profiles per point/side).
  4. `vector.edit.end`

---

## 8. Selection, Batch Rename, Alignment & Arrangement

- **Smart Selection & Search**:
  - Search without changing selection: `run_command {command: "node.find", params: {name: "Button", type: "instance"}}`.
  - Select by criteria: `select.byName {query: "Card", page: "all"}`, `select.matching` (`Ctrl+Alt+A`), `select.sameFill`, `select.sameStroke`, `select.sameEffect`, `select.sameText`, `select.sameFont`, `select.sameInstance`, `select.sameProperties`.
  - Find and replace text or layer names across the page: `edit.findReplace {find: "Sign in", replace: "Log in", layerNames: false}`.
- **Copy/Paste Properties & Replace**:
  - `edit.copyProperties {id: sourceId}` + `edit.pasteProperties {ids: [target1, target2]}` (`Ctrl+Alt+C` / `Ctrl+Alt+V`).
  - `edit.pasteOver` (`Ctrl+Shift+V`) and `edit.pasteReplace {ids: [oldId]}` (`Ctrl+Shift+R`).
- **Pattern & Regex Batch Rename (`object.batchRename`)**:
  - Supports `$&` (current name/match), `$1..$9` (regex capture groups), `$n` (ascending `1, 2, 3`), `$N` (descending), and `$nnn` (zero-padded `001, 002, 003`):
    ```json
    {
      "command": "object.batchRename",
      "params": {
        "ids": [10, 11, 12],
        "name": "Step $nn — $&",
        "start": 1
      }
    }
    ```
- **Alignment & Tidying**:
  - `align.left` (`Alt+A`), `align.hcenter` (`Alt+H`), `align.right` (`Alt+D`), `align.top` (`Alt+W`), `align.vcenter` (`Alt+V`), `align.bottom` (`Alt+S`).
  - `distribute.horizontal` (`Alt+Shift+H`), `distribute.vertical` (`Alt+Shift+V`), `arrange.tidy {ids, spacing: 24}` (`Ctrl+Alt+Shift+T`), `arrange.packH`, `arrange.packV`, `arrange.roundToPixels`.

# Files, Multi-Format Import/Export, Batch Data Fill, Plugins & `figcraft-cli`

Comprehensive agent guide for opening and saving files, importing assets from other design tools (Figma, Sketch, Penpot), configuring multi-format exports (PNG, JPEG, WebP, SVG, print-ready PDF, Android Vector Drawable XML, `.fig`, `.penpot`), generating batch data-driven creatives (`data.fill`), running sandboxed WASM plugins/widgets, and operating `figcraft-cli` in headless or attached mode.

---

## Table of Contents

1. [Document Lifecycle, Tabs, Windows & Recovery](#1-document-lifecycle-tabs-windows--recovery)
2. [Opening & Importing Files from Other Design Tools](#2-opening--importing-files-from-other-design-tools)
3. [Images, Presets, Filters & Non-Destructive Cropping](#3-images-presets-filters--non-destructive-cropping)
4. [Export Pipelines: Raster, SVG, Print PDF, Android XML & `.fig`](#4-export-pipelines-raster-svg-print-pdf-android-xml--fig)
5. [Data-Driven Batch Generation & Multi-Size Reflow (`data.fill`)](#5-data-driven-batch-generation--multi-size-reflow-datafill)
6. [Sandboxed WASM Plugins & Interactive Canvas Widgets (`plugin.*`, `widget.*`)](#6-sandboxed-wasm-plugins--interactive-canvas-widgets-plugin-widget)
7. [`figcraft-cli`, Headless MCP, Live `--attach`, & Folder Sandboxing](#7-figcraft-cli-headless-mcp-live---attach--folder-sandboxing)

---

## 1. Document Lifecycle, Tabs, Windows & Recovery

- **Create & Open**:
  - New design file: `run_command {command: "file.new", params: {name: "Mobile Banking"}}` (`Ctrl+N`).
  - New whiteboard: `run_command {command: "file.newBoard", params: {name: "Architecture Workshop"}}`.
  - New from starter template (`mobile-app`, `landing-page`, `dashboard`, `design-system`, `wireframe-kit`, `social-posts`, `slides`, `icon-set`):
    `run_command {command: "file.newFromTemplate", params: {template: "design-system", name: "Acme UI Kit"}}`.
  - Open existing file: `open_file {path: "/abs/path/file.figcraft", reload: false}` (if changed on disk since opened, returns `stale: true`; pass `reload: true` when the tab has no unsaved changes to reload it).
- **Save & Auto-Save**:
  - Native save: `save_file {path: "/abs/path/file.figcraft"}` (required on the first save of an untitled document; subsequent `save_file {}` calls reuse the path).
  - Save As / base64 download: `file.saveAs {path: "/abs/path/copy.figcraft"}` or `file.saveAs {data: true}`.
  - Enable automatic disk save (for files saved at least once): `run_command {command: "pref.autoSave", params: {on: true}}`.
  - Revert unsaved changes to last saved state on disk: `run_command {command: "file.revert"}`.
- **Multi-Tab & Multi-Window Management**:
  - List all open documents: `run_command {command: "doc.list"}` returns `[{index, id, name, dirty, active}]`.
  - Target any background open document without switching the front tab by passing `document: <id or path>` to `create_node`, `set_properties`, `batch`, `run_command`, `inspect_document`, `get_node`, `screenshot`, `export`, or `save_file`.
  - Switch active tab: `doc.switch {index: 1}`, `doc.nextTab` (`Ctrl+Tab`), `doc.previousTab` (`Ctrl+Shift+Tab`), `file.moveTab {from: 1, to: 0}`, `file.close {index: 1, force: true}`.
  - Manage pages within a document: `page.list`, `page.add {name: "Components"}` (a name starting with `"-"`, e.g., `"---"`, creates a page divider), `page.select {id}`, `page.rename`, `page.duplicate`, `page.move`, `page.delete`, `page.setBackground {color: "#0F172A"}`.

---

## 2. Opening & Importing Files from Other Design Tools

FigCraft natively opens and imports external formats on a best-effort basis and reports unsupported features in a `warnings` array:

| Source Format                                 | Open as New Tab (`open_file` / `file.open`) | Append/Merge into Current File (`file.import`) | Notes & Caveats                                                                                                                  |
| :-------------------------------------------- | :------------------------------------------ | :--------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| **FigCraft (`.figcraft`)**                    | Yes (lossless native format)                | Yes (appends pages, variables, flows)          | Native format.                                                                                                                   |
| **Figma (`.fig`) & FigJam (`.jam`)**          | Yes (best effort, returns `warnings`)       | Yes (appends pages, variables, flows)          | Always inspect `warnings` and verify visually via `screenshot`.                                                                  |
| **Figma REST API JSON (`.json`)**             | Yes (`variables` auto-loaded or passed)     | Yes (`variables` auto-loaded or passed)        | Automatically looks for `<name>.variables.json` or `variables.json` next to the file, or pass `variables` path/JSON explicitly.  |
| **Figma Clipboard HTML (`edit.pasteDesignLayers`)** | —                                     | Yes (`edit.pasteDesignLayers {html \| data}`)  | Pastes layers copied in Figma (`Ctrl+V`); returns `missingImages` if clipboard omitted image bytes.                              |
| **Sketch 48+ (`.sketch`)**                    | Yes (best effort, returns `warnings`)       | Yes (appends pages, variables, flows)          | Supports Sketch 48 or newer archives.                                                                                            |
| **Penpot (`.penpot`)**                        | Yes (best effort, returns `warnings`)       | Yes (appends pages, variables, flows)          | Can also export back to Penpot 2.x via `file.export {format: "penpot"}`.                                                         |
| **SVG (`.svg`)**                              | Yes (editable vector hierarchy)             | Yes (`center: true`, `x`, `y`)                 | Imports shapes, text, gradients, masks, and effects as an editable frame.                                                        |
| **Raster (`.png`, `.jpg`, `.webp`, `.gif`, `.tiff`)** | Yes (becomes an image layer)        | Yes (`file.placeImage` / `image.place`)        | Preserves embedded color profile (`imageProfile`).                                                                               |

---

## 3. Images, Presets, Filters & Non-Destructive Cropping

- **Place an Image on the Canvas or Inside an Existing Shape**:
  ```json
  {
    "command": "image.place",
    "params": {
      "path": "C:/path/to/photo.jpg",
      "target": heroCardId,
      "mode": "fill"
    }
  }
  ```
  (`mode`: `"fill" | "fit" | "crop" | "tile"`).
- **Replace Image While Keeping Crop & Adjustments**:
  `run_command {command: "image.replace", params: {ids: [heroCardId], path: "C:/path/to/new-photo.jpg"}}`.
- **Photographic Adjustments & Presets (`image.adjust`)**:
  - Built-in presets: `"vivid" | "muted" | "warm" | "cool" | "blackAndWhite" | "fade" | "reset"`.
  - Fine-grained filter sliders (`-1..1`): `{exposure, contrast, saturation, temperature, tint, highlights, shadows}`.
  - Save custom reusable presets in the document via `image.savePreset {name: "Brand Moody", filters: {...}}`.
- **Non-Destructive Crop (`image.crop`)**:
  - `run_command {command: "image.crop", params: {ids: [layerId]}}`.
- **Rasterize Complex Subtrees**:
  - `run_command {command: "object.rasterize", params: {ids: [layerId], scale: 2}}`.

---

## 4. Export Pipelines: Raster, SVG, Print PDF, Android XML & `.fig`

### Immediate Export (`export` MCP Tool / `file.export`)

Use the native `export` MCP tool (or `run_command {command: "file.export"}`) to export specific `ids` (or the current selection / top-level frames):

| Format     | Key Options & Capabilities                                                                                                                                            |
| :--------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `png`, `jpg`, `webp` | `scale` (`1..64`, default `1`) or `size` (`"2x"`, `"512w"`, `"512h"`), `contentsOnly` (default `true` ignores overlapping layers), `includeBoundingBox`.      |
| `svg`      | `svgOutlineText` (default `true`; set `false` to preserve `<text>` nodes), `svgIdAttribute` (layer names as `id`), `svgSimplifyStroke` (`stroke` attrs vs outlines). |
| `pdf`      | Print-ready options: `bleed` (points or `"3mm"`, `"0.125in"`), `cropMarks: true`, `bleedMarks: true`, `cmyk: true` (CMYK color conversion).                           |
| `xml`      | **Android Vector Drawable XML**: `vdCompat` (`"bestEffort"` approximates with warnings, `"exact"` omits unsupported with warnings, `"ignore"` writes without warnings), `svgIdAttribute` (`android:name`). |
| `fig`      | Experimental whole-file `.fig` export (also works by passing a `.fig` path to `save_file`). Returns `warnings` for features left out.                                 |
| `penpot`   | Whole-file Penpot 2.x archive export via `run_command {command: "file.export", params: {format: "penpot", path: "/abs/path/out.penpot"}}`.                            |

### Persistent Layer Export Presets & Multi-Page PDF Deck Export

- Attach reusable export configurations to layers via `export.add {ids: [iconId], setting: {format: "svg", suffix: ""}}` and `export.add {ids: [iconId], setting: {format: "png", size: "2x", suffix: "@2x"}}`.
- Batch-export every layer with export settings to a directory (slash names like `"icons/arrow-right"` automatically create subfolders):
  `run_command {command: "file.exportLayers", params: {dir: "C:/path/to/dist/assets"}}`
- Export all top-level frames on a page in reading order into a multi-page PDF presentation/print deck:
  `run_command {command: "file.exportFramesPdf", params: {path: "C:/path/to/deck.pdf", bleed: "3mm", cropMarks: true, cmyk: true}}`
- **Color Space Management**:
  - Set document color space (`"srgb" | "displayP3"`): `run_command {command: "file.colorProfile", params: {profile: "displayP3", convert: true}}`.
  - Soft-proof Display P3 out-of-gamut colors in sRGB: `run_command {command: "view.proofSrgb", params: {on: true}}`.

---

## 5. Data-Driven Batch Generation & Multi-Size Reflow (`data.fill`)

Generate up to **500 data-populated copies** of a template frame across multiple aspect ratios and export them to disk in **one undo step**:

```json
{
  "command": "data.fill",
  "params": {
    "id": templateFrameId,
    "rows": [
      {
        "name": "launch-announcement",
        "Headline": {"text": "FigCraft 1.0 Is Live", "fit": {"maxLines": 2, "orphans": true}},
        "Tag": {"text": "RELEASE", "fill": "#10B981"},
        "Badge": {"visible": true}
      },
      {
        "name": "workshop-invite",
        "Headline": {"text": "Join Our Design Systems Workshop", "fit": true},
        "Tag": {"text": "EVENT", "fill": "#3B82F6"},
        "Badge": {"visible": false}
      }
    ],
    "formats": [
      {"name": "square", "width": 1080, "height": 1080},
      {"name": "portrait", "width": 1080, "height": 1350},
      {"name": "story", "width": 1080, "height": 1920}
    ],
    "dir": "C:/path/to/campaigns/out",
    "format": "png",
    "scale": 1
  }
}
```

- Each row populates every descendant layer matching the key name (`"Headline"`, `"Tag"`, `"Badge"`).
- Each entry in `formats` resizes the copy so its Auto Layout reflows automatically and saves `<row.name>-<format.name>.<format>` into `dir`.

---

## 6. Sandboxed WASM Plugins & Interactive Canvas Widgets (`plugin.*`, `widget.*`)

Plugins run in a deterministic WebAssembly sandbox with **no access to the filesystem or network**, and every plugin/widget invocation executes as **one undo step**.

- **Manage & Run Plugins (`plugin.*`)**:
  - List installed plugins: `run_command {command: "plugin.list"}`.
  - Import from local manifest (`figcraft-plugin.json`): `run_command {command: "plugin.import", params: {path: "/abs/path/figcraft-plugin.json"}}`.
  - Browse & install from plugin directory server: `plugin.directory.list {query: "icon"}`, `plugin.directory.install {id: "plugin-id", confirm: true}`.
  - Execute a plugin command: `run_command {command: "plugin.run", params: {id: "plugin-id", command: "generate", params: {...}}}`.
  - Interact with an open plugin UI panel: `plugin.ui`, `plugin.event {id: "plugin-id", control: "submitBtn"}`, `plugin.close {id: "plugin-id"}`.
- **Interactive Canvas Widgets (`widget.*`)**:
  - Insert a widget onto the page: `widget.insert {plugin: "poll-widget", x: 200, y: 200}`.
  - Inspect active widgets and their click targets/fields/menus: `widget.list`.
  - Drive a widget programmatically: `widget.click {id: widgetId, target: "upvote"}`, `widget.setText {id: widgetId, field: "question", value: "Ship Friday?"}`, `widget.menu {id: widgetId, item: "theme", value: "dark"}`.

---

## 7. `figcraft-cli`, Headless MCP, Live `--attach`, & Folder Sandboxing

### Direct Command-Line Operations (`figcraft-cli`)

When executing shell tasks outside MCP, `figcraft-cli` provides standalone batch utilities:

```powershell
# Render a page to a high-DPI PNG image
figcraft-cli render landing.figcraft -o landing.png --scale 2

# Export every top-level frame as SVG into an output directory
figcraft-cli export landing.figcraft -o out/ --format svg

# Convert between formats (.fig, .sketch, .penpot, .figcraft) by extension
figcraft-cli convert design.fig design.figcraft

# Search all 636 engine commands and parameter schemas from the terminal
figcraft-cli commands --filter autoLayout
```

### Headless vs. Live Attached (`--control` / `--attach`) Modes

1. **Headless Mode (Default)**:
   - Started via `figcraft-cli mcp`. Runs an in-process engine session in the background with no GUI window.
2. **Live Attached Mode (Watch the Agent Work)**:
   - Start the desktop app with its localhost control port open: `figcraft --control 7979`
   - Connect the MCP server to the live window: `figcraft-cli mcp --attach 7979`
   - The agent appears in the app like a multiplayer peer with its own avatar, and FigCraft highlights the layers the agent modifies in real time.
   - Note on Linux (KDE/Wayland): keep the FigCraft window unminimized when using `--attach` (`#1906`).
3. **Filesystem Read/Write Sandboxing**:
   - Restrict an agent to specific directories with `--automation-read-root <dir>` and `--automation-write-root <dir>` (omit `--automation-write-root` to forbid disk writes completely).
   - When using `--attach 7979`, pass those flags to the `figcraft` app process itself rather than `figcraft-cli`.

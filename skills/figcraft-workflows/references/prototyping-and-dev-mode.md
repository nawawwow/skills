# Interactive Prototyping, Stateful Logic & Dev Mode Handoff

Comprehensive agent guide for wiring interactive prototypes (triggers, transitions, overlays, variables, conditional logic) and executing developer handoff in FigCraft (`inspect.code` across 10 languages/frameworks, `codeConnect`, `component.playground`, measurements, annotations, and diff comparisons).

---

## Table of Contents

1. [Prototype Flows & Device Settings](#1-prototype-flows--device-settings)
2. [Wiring Interactions, Triggers, Actions & Transitions](#2-wiring-interactions-triggers-actions--transitions)
3. [Stateful Prototypes: Variable Expressions & Conditionals](#3-stateful-prototypes-variable-expressions--conditionals)
4. [Presenting & Previewing Prototypes](#4-presenting--previewing-prototypes)
5. [Dev Mode Code Generation (`inspect.code` — 10 Frameworks)](#5-dev-mode-code-generation-inspectcode--10-frameworks)
6. [Code Connect (`codeConnect.*`) & Component Playground](#6-code-connect-codeconnect--component-playground)
7. [Measurements, Annotations, Dev Resources & Diff Comparison](#7-measurements-annotations-dev-resources--diff-comparison)

---

## 1. Prototype Flows & Device Settings

- **Add a Flow Starting Point**:
  - `run_command {command: "proto.flow.add", params: {start: homeFrameId, name: "Onboarding Flow"}}`
  - Rename or remove flows: `proto.flow.rename {start: homeFrameId, name: "Main Flow", description: "Happy path"}`, `proto.flow.remove {start: homeFrameId}`.
- **Configure Prototype Device & Responsive Viewport**:
  ```json
  {
    "command": "proto.settings",
    "params": {
      "device": "iPhone 16 Pro",
      "rotation": "portrait",
      "background": "#090D16",
      "responsive": true
    }
  }
  ```
  - Custom viewport size: pass `width` and `height` (`1..10000`) to automatically select `"Custom size"`.

---

## 2. Wiring Interactions, Triggers, Actions & Transitions

### Quick Click-Navigate Shorthand

To connect a button to a target screen with default click navigation:

```json
{
  "command": "proto.interaction.add",
  "params": {
    "id": getStartedButtonId,
    "dest": interestsScreenId,
    "transition": {
      "type": "smartAnimate"
    },
    "durationMs": 300,
    "easing": "easeOut"
  }
}
```

### Complete Triggers, Actions & Transitions Matrix

- **Triggers (`trigger.type`)**:
  - `"onClick"`, `"onHover"`, `"onPress"`, `"onDrag"`, `"mouseEnter"`, `"mouseLeave"`, `"mouseDown"`, `"mouseUp"` (supports `delayMs: 0..600000`).
  - `"afterDelay"`: `{"type": "afterDelay", "ms": 1500}` (for splash screens, auto-advancing carousels, or toasts).
  - `"keyPress"`: `{"type": "keyPress", "key": "Shift+K"}` or gamepad buttons (`"Gamepad A"`, `"Gamepad B"`, `"Gamepad X"`, `"Gamepad Y"`, `"Gamepad LB"`, `"Gamepad RB"`, `"Gamepad LT"`, `"Gamepad RT"`, `"Gamepad View"`, `"Gamepad Menu"`, `"Gamepad Up/Down/Left/Right/Home"`).
- **Actions (`action.type`)**:
  - `"navigate"`: `{type: "navigate", dest: frameId, preserveScroll: false}`
  - `"back"`: `{type: "back"}`
  - `"scrollTo"`: `{type: "scrollTo", dest: sectionId, offset: [0, -24]}`
  - `"openOverlay"`: `{type: "openOverlay", dest: modalFrameId, anchor: "screen" | "triggerInside" | "triggerOutside", position: "center", close_on_outside: true, background: "#00000066"}`
  - `"swapOverlay"`: `{type: "swapOverlay", dest: otherModalId}`
  - `"closeOverlay"`: `{type: "closeOverlay"}`
  - `"openUrl"`: `{type: "openUrl", url: "https://craft.wiki", openInNewTab: true}`
  - `"changeTo"`: `{type: "changeTo", dest: hoverVariantId}` (interactive component state switching between variants)
  - `"setVariable"`: `{type: "setVariable", variable: "cartCount", expression: "cartCount + 1"}`
  - `"setVariableMode"`: `{type: "setVariableMode", collection: "Theme", mode: "Dark"}`
  - `"conditional"`: `{type: "conditional", blocks: [...]}`
- **Transitions (`transition.type`)**:
  - `"instant"`, `"dissolve"`, `"smartAnimate"`, `"moveIn"`, `"moveOut"`, `"push"`, `"slideIn"`, `"slideOut"` (with `direction: "left" | "right" | "top" | "bottom"`).
- **Easing Curves (`easing`)**:
  - Presets: `"linear"`, `"easeIn"`, `"easeOut"`, `"easeInOut"`, `"easeInBack"`, `"easeOutBack"`, `"easeInOutBack"`, `"gentle"`, `"quick"`, `"bouncy"`, `"slow"`.
  - Custom Bezier: `{"customBezier": {"x1": 0.22, "y1": 1, "x2": 0.36, "y2": 1}}`.
  - Custom Spring: `{"customSpring": {"mass": 1, "stiffness": 300, "damping": 24}}`.

---

## 3. Stateful Prototypes: Variable Expressions & Conditionals

### Chaining Multiple Actions with Conditionals

An interaction can execute a sequence of `actions` (e.g., increment a tap counter and then branch based on the count):

```json
{
  "command": "proto.interaction.add",
  "params": {
    "id": submitButtonId,
    "trigger": {"type": "onClick"},
    "actions": [
      {
        "type": "setVariable",
        "variable": "attempts",
        "expression": "attempts + 1"
      },
      {
        "type": "conditional",
        "blocks": [
          {
            "expression": "attempts >= 3",
            "actions": [
              {"type": "navigate", "dest": lockedOutFrameId}
            ]
          },
          {
            "actions": [
              {"type": "navigate", "dest": dashboardFrameId}
            ]
          }
        ]
      }
    ],
    "transition": {"type": "smartAnimate"},
    "durationMs": 250
  }
}
```

### Fine-Grained Action & Conditional Editing

- Append, edit, reorder, or remove individual actions within an interaction: `proto.action.add`, `proto.action.set`, `proto.action.move`, `proto.action.remove`.
- Add or edit `else if` / `else` branches: `proto.conditional.addBlock`, `proto.conditional.setCondition`, `proto.conditional.removeBlock`.
- **Dry-Run Expression Evaluation (`proto.evaluate`)**:
  Test any prototype expression against a layer's active variable modes without changing the document:
  ```json
  {
    "command": "proto.evaluate",
    "params": {
      "expression": "attempts + 1",
      "id": submitButtonId
    }
  }
  ```

---

## 4. Presenting & Previewing Prototypes

- **Full-Window Presenter**: `run_command {command: "proto.present", params: {start: homeFrameId}}` (`Ctrl+Alt+Enter` / `⌥⌘Enter`).
  - Presenter keyboard navigation: `→`, `Space`, or `N` (next frame), `←` (previous frame), `R` (restart flow), `F` (fullscreen).
- **Live Canvas Preview Pane**: `run_command {command: "proto.preview", params: {start: homeFrameId}}` (`Shift+Space`); close via `proto.closePreview`.
- **Presentation Options**: `run_command {command: "proto.presentOptions", params: {scale: "fit", deviceFrame: true, hotspotHints: true, inspect: false, hideUi: false}}`.

---

## 5. Dev Mode Code Generation (`inspect.code` — 10 Frameworks)

In the GUI, `Shift+D` (`view.devMode`) switches to read-only Dev Mode. Programmatically, AI agents can invoke all `inspect.*` commands at any time without locking the editor!

### Generating Code for Any Layer or Screen (`inspect.code`)

```json
{
  "command": "inspect.code",
  "params": {
    "id": screenFrameId,
    "language": "tailwind",
    "mobile": mobileScreenFrameId,
    "unit": "rem",
    "rootFontSize": 16
  }
}
```

**Supported `language` Targets (10 Targets)**:
1. `"css"`: Standard CSS layout, typography, variables, and visual properties.
2. `"html"`: Full layer subtree rendered as semantic HTML + CSS.
3. `"react"`: Full layer subtree as a React component (component properties become React props; instances pass prop values).
4. `"tailwind"`: React + **Tailwind CSS v4** utilities (fluid auto-layout flex/grid classes, inlined instances with overrides, bound variables mapped to `@theme` utilities; pass `mobile: mobileFrameId` with matching layer names to generate mobile-first responsive markup with desktop overrides under `lg:`).
5. `"vue"`: Single-File Component (SFC) template + styles for the subtree.
6. `"leptos"`: Rust `view!` macro markup for Leptos web applications.
7. `"swiftui"`: Apple SwiftUI declarative views (`VStack`, `HStack`, modifiers).
8. `"compose"`: Android Jetpack Compose `@Composable` Kotlin functions.
9. `"arkui"`: HarmonyOS ArkTS declarative UI components.
10. `"flutter"`: Dart Flutter widget tree (`Column`, `Row`, `Container`, `Text`).

### Inspecting Structured Properties & Exportable Assets

- **Structured Property Table**: `run_command {command: "inspect.properties", params: {id: layerId, colorFormat: "hex"}}` (returns layout, auto layout, typography, fills, strokes, and effects with bound style/variable token names).
- **Component Definition & Usage Snippet**: `run_command {command: "inspect.componentCode", params: {id: compOrInstId, language: "react"}}`.
- **Discover Exportable Handoff Assets**: `run_command {command: "inspect.assets", params: {ids: [screenFrameId]}}` (identifies layers with export settings, small vector icons as SVG, and raster images as PNG). Export all of them at once with `run_command {command: "file.exportLayers", params: {ids: [screenFrameId], assets: true, dir: "/abs/path/assets"}}`.

---

## 6. Code Connect (`codeConnect.*`) & Component Playground

### Linking Design Components to Production Code (`codeConnect.*`)

Connect a FigCraft component or component set to its real repository import and template so `inspect.code` and `inspect.componentCode` output production usages instead of raw generated markup:

```json
{
  "command": "codeConnect.set",
  "params": {
    "id": buttonSetId,
    "language": "react",
    "importPath": "@/components/ui/Button",
    "name": "Button",
    "template": "<Button variant=\"{Style}\" disabled={State ? \"true\" : \"false\"}>{Label}</Button>"
  }
}
```

- **Export/Import Connections to Repository (`figcraft.connect.json`)**:
  - `run_command {command: "codeConnect.export", params: {path: "/abs/path/repo/figcraft.connect.json"}}`
  - `run_command {command: "codeConnect.import", params: {path: "/abs/path/repo/figcraft.connect.json"}}`
  - Remove a link: `run_command {command: "codeConnect.remove", params: {id: buttonSetId, language: "react"}}`.

### Non-Destructive Component Playground (`component.playground`)

Test any combination of component properties, render a preview PNG, and retrieve the resulting code snippet **without mutating the document**:

```json
{
  "command": "component.playground",
  "params": {
    "id": buttonSetId,
    "properties": {
      "Style": "Primary",
      "State": "Hover",
      "Label": "Deploy Now"
    },
    "language": "react",
    "path": "C:/path/to/button-hover-preview.png",
    "scale": 2
  }
}
```

---

## 7. Measurements, Annotations, Dev Resources & Diff Comparison

- **Ready-for-Dev Workflow & Version Diffing**:
  1. Mark a screen ready for engineering: `set_properties {ids: [frameId], props: {devStatus: "readyForDev", devNote: "Approved in design review"}}`.
  2. Query screens by handoff status: `run_command {command: "inspect.readyForDev", params: {status: "readyForDev"}}` (`"readyForDev" | "changed" | "completed" | "any"`).
  3. Compare what changed since a frame was marked ready (or against a saved version ID):
     `run_command {command: "dev.compare", params: {id: frameId}}`
  4. Resolve change flag after developer review: `run_command {command: "dev.resolveChange", params: {ids: [frameId], reason: "Updated copy spacing"}}`.
  5. Isolate a ready-for-dev frame on the canvas: `dev.focus {id: frameId}` / `dev.unfocus`.
- **Canvas Measurements (`devMode.*` & `measure.*`)**:
  - Measure distance between two layers (like `Alt`-hover): `run_command {command: "measure.distances", params: {ids: [layerA], to: layerB}}`.
  - Measure auto-layout padding and gaps (like `Shift+Alt`-hover): `run_command {command: "measure.padding", params: {id: autoLayoutFrameId}}`.
  - Pin persistent measurement lines on the canvas: `run_command {command: "devMode.addMeasurement", params: {from: layerA, to: layerB}}` (`devMode.measurements` lists them, `devMode.removeMeasurement` deletes them).
- **Canvas Annotations & Categories (`annotation.*`)**:
  - Create custom categories (e.g., `"Accessibility"`, `"Motion"`): `run_command {command: "annotation.addCategory", params: {name: "Accessibility", color: "#10B981"}}`.
  - Pin a note and live property callouts to a layer:
    ```json
    {
      "command": "annotation.add",
      "params": {
        "id": buttonId,
        "label": "Maintain 44px minimum touch target height on mobile",
        "properties": ["height", "padding", "fill", "cornerRadius"],
        "category": "Accessibility"
      }
    }
    ```
- **Developer Links (`devResource.*`)**:
  - Attach specification URLs, Storybook links, or Jira tickets to a layer or main component:
    `run_command {command: "devResource.add", params: {id: buttonSetId, name: "Storybook — Button", url: "https://storybook.example.com/?path=/docs/button"}}`.

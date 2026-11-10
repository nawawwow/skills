# Components, Variants, Slots, Styles, Variables & Libraries

Comprehensive agent guide for architecting scalable design systems in FigCraft: reusable components, variant sets, slots, component properties, shared styles, multi-mode variables (Light/Dark themes, aliases, color calculations, token export), and team libraries.

---

## Table of Contents

1. [Components & Instances Lifecycle](#1-components--instances-lifecycle)
2. [Variant Sets & Component Properties](#2-variant-sets--component-properties)
3. [Component Slots (`component.makeSlot`)](#3-component-slots-componentmakeslot)
4. [Styles (`paint`, `text`, `effect`, `grid`)](#4-styles-paint-text-effect-grid)
5. [Variables, Modes (Light/Dark), Aliases & Color Calculations](#5-variables-modes-lightdark-aliases--color-calculations)
6. [Developer Token Export & Import (JSON, CSS, Tailwind v4, Flutter)](#6-developer-token-export--import-json-css-tailwind-v4-flutter)
7. [Publishing & Consuming Libraries](#7-publishing--consuming-libraries)

---

## 1. Components & Instances Lifecycle

### Creating Main Components

- **Single Component**:
  - Create directly via `create_node {type: "component", name: "Button", width: 120, height: 44, props: {...}}`.
  - Or convert an existing frame/group/selection via `run_command {command: "component.create", params: {ids: [frameId]}}` (`Ctrl+Alt+K` / `⌥⌘K`).
- **Multiple Components at Once**:
  - Turn each layer in `ids` into its own standalone component: `run_command {command: "component.createMultiple", params: {ids: [icon1, icon2, icon3]}}`.
- **Listing All Components**:
  - `run_command {command: "component.list"}` returns `[{id, name, type, page, instances, folder, label, library}]` (slash-separated names like `"Form/Input/Text"` organize components into folders in the Assets panel).

### Placing & Managing Instances

- **Instantiate**:
  - Exact parent & local coordinates: `run_command {command: "instance.create", params: {component: compId, parent: frameId, x: 24, y: 24}}`.
  - Drop at a page point (auto-inserts into the frame or auto-layout flow underneath): `run_command {command: "instance.place", params: {component: compId, x: 200, y: 300}}`.
  - Note: Duplicating a main component (`edit.duplicate`) creates an **instance** of it (unless the component is a variant inside a component set, where duplicating creates a new variant in that set).
- **Instance Overrides & Maintenance**:
  - Switch variants or set properties: `run_command {command: "instance.setProperties", params: {ids: [instId], properties: {"Style": "Primary", "State": "Hover", "Label": "Continue"}}}`.
  - Swap to another component: `run_command {command: "instance.swap", params: {ids: [instId], component: otherCompId}}` (or `instance.swapAt` at page coordinates, preserving text overrides by matching layer names).
  - Reset all changes: `run_command {command: "component.resetInstance", params: {ids: [instId]}}`.
  - Reset specific override group: `run_command {command: "component.resetOverride", params: {id: instId, group: "fills"}}` (`fills | strokes | effects | opacity | visible | name | corners | characters | textStyle | padding | gap | alignment | grids | exports | interactions | size | position | modes | component | props | slot`).
  - Push instance overrides back to the main component: `run_command {command: "component.pushChanges", params: {id: instId}}`.
  - Restore a deleted main component from a surviving instance: `run_command {command: "component.restoreMain", params: {id: instId}}`.
  - Detach instance into a regular frame: `run_command {command: "component.detach", params: {ids: [instId]}}` (`Ctrl+Alt+B`).

---

## 2. Variant Sets & Component Properties

### Building Variant Sets

1. **Combine Separate Components into Variants**:
   - Name components using `Property=Value` pairs (e.g., `"Style=Primary, State=Default"`, `"Style=Secondary, State=Default"`) or let FigCraft assign defaults, then run:
     ```json
     {
       "command": "component.combineVariants",
       "params": {
         "ids": [compPrimaryId, compSecondaryId]
       }
     }
     ```
2. **Add a Variant to an Existing Component or Set**:
   - `run_command {command: "component.addVariant", params: {id: compOrSetId, property: "State", value: "Disabled"}}`.

### Defining Component Properties (`component.addProperty`)

Expose configurable props on a component or component set so instances can be customized cleanly (and so Dev Mode generates typed component props):

| Property `type` | Bound Target (`layer` / `field`)          | Example `component.addProperty` Call                                                                                     |
| :-------------- | :---------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| `boolean`       | Layer visibility (`field: "visible"`)     | `{"command": "component.addProperty", "params": {"id": setId, "name": "Show Icon", "type": "boolean", "layer": iconId}}` |
| `text`          | Text content (`field: "characters"`)      | `{"command": "component.addProperty", "params": {"id": setId, "name": "Label", "type": "text", "layer": textNodeId}}`    |
| `instanceSwap`  | Nested instance (`field: "mainComponent"`)| `{"command": "component.addProperty", "params": {"id": setId, "name": "Icon", "type": "instanceSwap", "layer": nestedInstId, "preferred": [iconA, iconB]}}` |
| `variant`       | Component set variant axis                | `{"command": "component.addProperty", "params": {"id": setId, "name": "Size", "type": "variant", "default": "md"}}`      |
| `slot`          | Child frame inside component (`field: "slot"`) | `{"command": "component.addProperty", "params": {"id": setId, "name": "Body", "type": "slot", "layer": slotFrameId}}` |

- Bind additional layers inside variants to an existing property via `component.bindProperty {layer: otherLayerId, property: "Label", field: "characters"}`.
- Bubble up a nested instance's own properties onto the parent component via `component.exposeInstance {id: nestedInstanceId, exposed: true}`.
- Inspect all property definitions and current values with `component.properties {id: compOrInstId}`.

---

## 3. Component Slots (`component.makeSlot`)

Slots let instances inject arbitrary custom children into a designated frame inside a component without detaching the instance:

1. **Mark a Child Frame Inside a Main Component as a Slot**:
   ```json
   {
     "command": "component.makeSlot",
     "params": {
       "id": innerContentFrameId,
       "name": "Card Content",
       "preferred": [chartComponentId, tableComponentId]
     }
   }
   ```
2. **Insert Content into an Instance's Slot**:
   ```json
   {
     "command": "instance.slotInsert",
     "params": {
       "id": cardInstanceId,
       "slot": "Card Content",
       "component": chartComponentId,
       "replace": true
     }
   }
   ```
3. **Reset a Slot Back to Main Component Default**:
   `run_command {command: "instance.resetSlot", params: {id: cardInstanceId, slot: "Card Content"}}`.

---

## 4. Styles (`paint`, `text`, `effect`, `grid`)

Styles store reusable visual configurations under a hierarchical slash name (e.g., `"Brand/Primary"`, `"Heading/H1"`):

- **Create from an Existing Layer or Explicit JSON**:
  - `run_command {command: "style.create", params: {type: "paint", name: "Surface/Elevated", from: cardNodeId}}`
  - `run_command {command: "style.create", params: {type: "text", name: "Body/Regular", from: textNodeId}}`
- **Apply & Detach**:
  - `run_command {command: "style.apply", params: {ids: [node1, node2], style: "Surface/Elevated", target: "fill"}}`
  - `run_command {command: "style.detach", params: {ids: [node1], which: "fill"}}`
- **Bind a Variable Inside a Style (`style.bind`)**:
  - Connect a style property to a mode-aware variable:
    `run_command {command: "style.bind", params: {style: "Surface/Elevated", field: "fill", variable: "color/bg/elevated"}}`
- **Organize & List**:
  - `style.list {type: "paint"}`, `style.update`, `style.duplicate`, `style.move {styles: [...], folder: "Brand/Core"}`, `style.renameFolder`, `style.delete`.

---

## 5. Variables, Modes (Light/Dark), Aliases & Color Calculations

### Creating Multi-Mode Collections & Variables

Build a complete Light/Dark token architecture in one `batch`:

```json
{
  "label": "Create Theme Variables",
  "commands": [
    {
      "command": "variable.createCollection",
      "as": "theme",
      "params": {
        "name": "Theme",
        "modes": ["Light", "Dark"]
      }
    },
    {
      "command": "variable.create",
      "as": "bgSurface",
      "params": {
        "collection": {"$ref": "theme"},
        "name": "color/bg/surface",
        "type": "color",
        "values": {
          "Light": "#FFFFFF",
          "Dark": "#0F172A"
        }
      }
    },
    {
      "command": "variable.create",
      "as": "textPrimary",
      "params": {
        "collection": {"$ref": "theme"},
        "name": "color/text/primary",
        "type": "color",
        "values": {
          "Light": "#0F172A",
          "Dark": "#F8FAFC"
        }
      }
    },
    {
      "command": "variable.create",
      "params": {
        "collection": {"$ref": "theme"},
        "name": "radius/card",
        "type": "number",
        "values": {
          "Light": 16,
          "Dark": 16
        }
      }
    }
  ]
}
```

### Advanced Variable Values: Aliases, Alpha & Color Mixes

In `variable.create` and `variable.set`, values can be dynamic references instead of literals:
- **Alias**: `{"alias": "primitive/blue/600"}` (references another variable of the same type).
- **Alpha Calculation** (`color` variables): `{"alpha": {"variable": "color/text/primary", "opacity": 0.6}}` (uses the referenced variable's color with its alpha replaced by `0.6`).
- **Channel Mix Calculation** (`color` variables): `{"mix": {"from": {"variable": "color/bg/surface"}, "to": {"literal": "#3B82F6"}, "t": 0.12}}` (blends 12% brand tint into the active mode's surface color).

### Binding Variables & Switching Modes

- **Inline Binding in `set_properties`**:
  - For fills and strokes: `set_properties {ids: [cardId], props: {fill: {"$var": "color/bg/surface"}, stroke: {"$var": "color/text/primary"}}}`.
- **General Property Binding (`variable.bind`)**:
  - Bind any supported property (`fill`, `stroke`, `fills/0/color`, `fills/0/stops/0/color`, `effects/0/color`, `effects/0/radius`, `layoutGrids/0/gutter`, `componentProperties/Label`, `width`, `height`, `opacity`, `cornerRadius`, `gap`, `paddingHorizontal`, `characters`, `visible`, `fontSize`, etc.):
    `run_command {command: "variable.bind", params: {ids: [cardId], field: "cornerRadius", variable: "radius/card"}}`
- **Switch Frame or Page Theme Mode (`variable.setMode`)**:
  - Preview a screen in Dark mode: `run_command {command: "variable.setMode", params: {ids: [screenFrameId], collection: "Theme", mode: "Dark"}}` (`mode: null` resets to `"Auto"`, inheriting from parent).
- **Extended Collections (`variable.extendCollection`)**:
  - Derive a brand/sub-theme collection that inherits and tracks an existing collection's variables and modes while allowing per-mode overrides (`variable.resetOverride` restores inherited values).

---

## 6. Developer Token Export & Import (JSON, CSS, Tailwind v4, Flutter)

Export variables directly to code or files using `variable.export`:

| `format`     | Output Specification                                                                                                                    |
| :----------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| `"json"`     | FigCraft / Figma-compatible local variables JSON (`variableCollections` and `variables`) ready for `variable.import`.                   |
| `"css"`      | Standard CSS custom properties (`:root` for default mode, `[data-<collection>="<mode>"]` for alternate modes).                          |
| `"tailwind"` | **Tailwind CSS v4** `@theme` block naming tokens `--color-*`, `--radius-*`, `--text-*`, `--spacing-*`, `--font-*` (matching `inspect.code`). |
| `"dart"`     | Strongly typed **Flutter** Dart constant classes (`Color`, `double`, `String`, `bool`) per collection and mode.                         |

```json
{
  "command": "variable.export",
  "params": {
    "format": "tailwind",
    "path": "C:/path/to/project/src/styles/tokens.css"
  }
}
```

Import or update variable collections from JSON via `run_command {command: "variable.import", params: {variables: "/abs/path/tokens.json"}}` (returns `{collections, variables, updated, warnings}`).

---

## 7. Publishing & Consuming Libraries

- **Hide Internal Helpers from Publishing**:
  - Prefix component names with `.` or `_`, or run `run_command {command: "component.hideWhenPublishing", params: {ids: [helperCompId], on: true}}`.
  - For variables, set `variable.update {variable: varId, hiddenFromPublishing: true}`.
- **Publish Library**:
  - Local file library: `run_command {command: "library.publish", params: {description: "v1.2 Button & Dark Mode tokens"}}` followed by `save_file`.
  - Server-hosted team library: `run_command {command: "library.publishToServer", params: {server: "wss://...", description: "v1.2"}}`.
- **Consume in Other Files**:
  - Link a published `.figcraft` file or server link: `run_command {command: "library.add", params: {path: "/abs/path/design-system.figcraft"}}`.
  - Use library assets: `library.place`, `library.swapAt`, `library.import`, `library.applyStyle`, `library.bindVariable`, `library.aliasVariable`, `library.setVariableMode`, `library.extendCollection`.
  - Check and pull library updates: `library.updates`, `library.check`, `library.acceptUpdates`, `library.swap` (re-points all instances/styles/variables from one library to another), `library.usage` (tracks insertions and detachments).

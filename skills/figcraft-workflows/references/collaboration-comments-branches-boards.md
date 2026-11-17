# Collaboration: Comments, Version History, Branches, Live Sessions & Boards

Comprehensive agent guide for managing design feedback loops (`comment.*` + `wait_for_changes`), version checkpoints (`version.*`), safe branching & merge conflict resolution (`branch.*`), multiplayer live sessions (`collab.*`), and interactive whiteboard workshops (`board.*`).

---

## Table of Contents

1. [Comments & Reactive Feedback Loop (`comment.*` + `wait_for_changes`)](#1-comments--reactive-feedback-loop-comment--wait_for_changes)
2. [Version History & Checkpoints (`version.*`)](#2-version-history--checkpoints-version)
3. [Design Branching, Diff Review & Conflict Resolution (`branch.*`)](#3-design-branching-diff-review--conflict-resolution-branch)
4. [Live Sessions & Multiplayer Collaboration (`collab.*`)](#4-live-sessions--multiplayer-collaboration-collab)
5. [Workshop Boards: Stickies, Connected Shapes, Templates, Timers & Voting (`board.*`)](#5-workshop-boards-stickies-connected-shapes-templates-timers--voting-board)

---

## 1. Comments & Reactive Feedback Loop (`comment.*` + `wait_for_changes`)

### End-to-End Comment Resolution Protocol

When asked to review or fix comments on a document:

1. **List Open Comment Threads**:
   - Call `run_command {command: "comment.list", params: {page: "all", filter: "open"}}` (or read `figcraft://comments`, or call `comment.prompt {page: "all", filter: "open"}`).
   - Each thread reports its `id`, `page`, `x`, `y`, `anchor` (pinned layer/frame ID), initial message (`text`, `author`, `mentions`), and `replies`.
2. **Inspect the Anchored Target**:
   - Call `get_node {id: anchorNodeId, depth: 3}` and `screenshot {ids: [anchorNodeId]}` to understand the visual context around the pin.
3. **Apply the Design Fix**:
   - Execute the required mutations via `set_properties`, `batch`, or `run_command`, then verify with `inspect_document` and `screenshot`.
4. **Reply First, Then Resolve**:
   - **CRITICAL INVARIANT**: Replying to a resolved comment thread **reopens** it. Always post your explanation via `comment.reply` _before_ calling `comment.resolve`:

     ```json
     {
       "label": "Reply and Resolve Comment",
       "commands": [
         {
           "command": "comment.reply",
           "params": {
             "id": 1,
             "text": "Increased button horizontal padding to 24px and updated fill to Brand/Primary."
           }
         },
         {
           "command": "comment.resolve",
           "params": {
             "id": 1,
             "resolved": true
           }
         }
       ]
     }
     ```

### Watching for Real-Time Feedback (`wait_for_changes`)

In an attached FigCraft app session (`figcraft --control 7979` + `figcraft-cli mcp --attach 7979`), use the native `wait_for_changes` MCP tool to react to new comments as reviewers post them:

1. Call `wait_for_changes {after: 0, timeoutMs: 20000, topics: ["comments"]}`.
2. Process any returned events (each event includes a sequence number and thread `id`).
3. Call `wait_for_changes {after: returnedCursor, timeoutMs: 20000}` again to continue watching without missing intermediate events. (Note: in headless mode with no other writer, `wait_for_changes` returns immediately.)

### Additional Comment Commands

- Pin a new comment to a frame: `comment.add {x: 180, y: 240, text: "Check contrast against Dark mode", anchor: true}`.
- Add emoji reaction: `comment.react {id: 1, emoji: "👍"}`.
- Step through threads or zoom to pins: `comment.open {id: 1, view: "fit"}`, `comment.next {filter: "open"}`, `comment.zoom {ids: [1, 2]}`, `comment.markRead`.

---

## 2. Version History & Checkpoints (`version.*`)

Create named checkpoints before major structural refactors so users can compare or roll back effortlessly:

- **Save a Named Version Checkpoint**:
  `run_command {command: "file.saveVersion", params: {name: "Pre-Grid Refactor", description: "Baseline 3-column card layout"}}` (`Ctrl+Alt+S` / `⌥⌘S`).
- **List Version History**:
  `run_command {command: "version.list"}` returns `[{id, index, name, description, time, auto, previewing}]` (the app also creates automatic checkpoints every 30 minutes via `version.autosave`, keeping the newest 20 autosaves).
- **Compare, Preview, Duplicate, or Restore**:
  - Diff a frame against any historical version: `run_command {command: "dev.compare", params: {id: frameId, version: versionId}}`.
  - Read-only canvas preview: `version.preview {id: versionId}` → exit with `version.exitPreview`.
  - Branch a historical version into a new document tab: `version.duplicate {id: versionId}`.
  - Restore version into the active document (as one undo step, preserving current state in history first): `version.restore {id: versionId}`.

---

## 3. Design Branching, Diff Review & Conflict Resolution (`branch.*`)

A branch is an isolated working copy stored inside the file that opens in its own tab. In live sessions, a branch stays private to its creator until merged.

### Complete Branching & Merge Lifecycle

```text
branch.create ──► Mutate on Branch Tab ──► branch.review ──► (Optional) branch.updateFromMain ──► branch.merge
```

1. **Create & Switch to a Branch**:

   ```json
   {
     "command": "branch.create",
     "params": {
       "name": "feat/checkout-redesign"
     }
   }
   ```

   Returns `{id, name, index}` and switches to the new branch tab (`index`).

2. **List or Reopen Existing Branches**:
   - `run_command {command: "branch.list"}` (`state: "active" | "merged" | "archived"`).
   - `run_command {command: "branch.open", params: {id: branchId}}`.
3. **Review Differences & Detect Conflicts (`branch.review`)**:
   - `run_command {command: "branch.review", params: {id: branchId}}` returns changes made on `branch` and `main` since the branch base, plus an array of `conflicts: [{key, id, name, property, branch, main, deletedBy}]` whenever the same property was modified on both sides or a layer was deleted on one side and edited on the other.
4. **Sync Upstream Changes from Main (`branch.updateFromMain`)**:
   - If `main` changed while working on the branch, pull `main` into the branch first. If `branch.review` reported conflicts, every conflict key must be resolved explicitly (`"branch"` or `"main"`):

     ```json
     {
       "command": "branch.updateFromMain",
       "params": {
         "id": branchId,
         "resolutions": {
           "14:fills": "branch",
           "22:characters": "main"
         }
       }
     }
     ```

5. **Merge into Main (`branch.merge`) or Archive (`branch.archive`)**:
   - Merge back as **one undo step** on `main` (automatically archiving the branch):

     ```json
     {
       "command": "branch.merge",
       "params": {
         "id": branchId,
         "resolutions": {
           "14:fills": "branch"
         }
       }
     }
     ```

   - Or set aside without merging: `run_command {command: "branch.archive", params: {id: branchId}}`.

---

## 4. Live Sessions & Multiplayer Collaboration (`collab.*`)

FigCraft supports real-time multiplayer editing either via a collaboration server (`Online`, default `collab.craftapps.dev` or a self-hosted `figcraft-server`) or peer-to-peer on a `Local network` (`LAN`).

- **Share a File with a Join Code or Link (`collab.share`)**:
  - Online (supports `"edit" | "comment" | "view"` access):
    `run_command {command: "collab.share", params: {via: "online", access: "edit"}}`
  - Local network (peer-to-peer while app stays open; everyone who joins can edit):
    `run_command {command: "collab.share", params: {via: "local", bind: "lan"}}`
- **Join a Session (`collab.join`)**:
  - `run_command {command: "collab.join", params: {code: "K7M-2QX-9TD"}}` (or pass a `figcraft://join?...` invite `link`).
- **Inspect Session & Peers (`collab.peers`)**:
  - `run_command {command: "collab.peers"}` returns connection `status` (`"off" | "connecting" | "live" | "reconnecting" | "failed"`), join `code`, `share` links, and active `peers` with their live cursor coordinates and selections.
- **Multiplayer Presence & Facilitation**:
  - Follow a peer's viewport: `collab.follow {client: peerId}` (omit `client` to stop following).
  - Request everyone to follow your viewport: `collab.spotlight {on: true}`.
  - Broadcast a cursor chat bubble (`/` shortcut, fades after 5s): `collab.cursorChat {text: "Reviewing header spacing here"}`.
  - Show agent pointer on the shared canvas: `collab.cursor {x: 320, y: 180}`.
- **Stop Sharing or Remove from Server**:
  - Revoke public join codes/links: `collab.stop`.
  - Delete an online file permanently from the server: `collab.manageFile {file: fileId, action: "remove"}`.
  - Note on public server limits: the default public server stores files unencrypted, deletes files unopened for 30 days, and caps total hosted files at 1000 (`"the server keeps at most 1000 files"`). For confidential work or when the public server is full, use `via: "local"` or self-host `figcraft-server`.

---

## 5. Workshop Boards: Stickies, Connected Shapes, Templates, Timers & Voting (`board.*`)

A Board (`file.newBoard`) is a dedicated collaborative whiteboard document with sticky notes (`Q`), flowchart shapes (`B`), smart connectors (`X`), freehand markers (`M`), highlighters (`U`), stamps (`W`), tables, timers, and dot-voting sessions.

### Creating a Board & Instantiating Workshop Templates

1. **Create a New Board**:
   `run_command {command: "file.newBoard", params: {name: "Sprint 14 Retrospective"}}`
2. **Insert a Built-In Workshop Template (`board.template`)**:
   - Available templates (`board.templates`):
     - `"retrospective"` (`1280×592`: Went well, To improve, Next steps)
     - `"brainstorm"` (`1344×760`: Central question with 4 idea clusters)
     - `"weeklyPlanner"` (`1380×632`: Columns for each working day)
     - `"flowChart"` (`1220×360`: Steps, decision diamond, and two outcomes joined by connectors)
     - `"kanban"` (`900×812`: To do, Doing, Done columns with cards)
   - Instantiate: `run_command {command: "board.template", params: {name: "retrospective", x: 0, y: 0}}`.

### Adding Stickies, Connected Flowchart Nodes, Tables & Stamps

- **Sticky Notes (`board.sticky` & `board.nextSticky`)**:
  - Create a sticky (`color`: `"yellow" | "orange" | "red" | "pink" | "violet" | "blue" | "green" | "gray"` or `#hex`):
    `run_command {command: "board.sticky", params: {x: 100, y: 120, text: "Automate release notes", color: "yellow", author: "Product Team"}}`
  - Chain an adjacent sticky note (`Shift+Cmd+Enter`):
    `run_command {command: "board.nextSticky", params: {id: stickyId, side: "right"}}`
- **Flowchart Shapes & Auto-Connected Diagrams (`board.shape` & `board.addConnected`)**:
  - Supported `shape` types (23 shapes): `"rectangle"`, `"roundedRectangle"`, `"ellipse"`, `"diamond"`, `"triangle"`, `"triangleDown"`, `"parallelogramRight"`, `"parallelogramLeft"`, `"trapezoid"`, `"pentagon"`, `"hexagon"`, `"octagon"`, `"star"`, `"plus"`, `"arrowLeft"`, `"arrowRight"`, `"chevron"`, `"speechBubble"`, `"database"`, `"document"`, `"predefinedProcess"`, `"manualInput"`, `"internalStorage"`.
  - Spawn the next connected flowchart step automatically on any side (`"right" | "below" | "left" | "above"`):

    ```json
    {
      "command": "board.addConnected",
      "params": {
        "id": startShapeId,
        "side": "right"
      }
    }
    ```

  - Wire arbitrary layers with smart connectors (`"straight" | "elbow" | "curved"`):
    `run_command {command: "board.connector", params: {from: nodeA, to: nodeB, style: "elbow", label: "Yes"}}` (adjust with `board.reattach`, `board.reshape`, `board.label`).
- **Tables, Stamps & Ink**:
  - Create a populated table in one call: `run_command {command: "board.table", params: {x: 100, y: 600, cells: [["Task", "Owner", "Status"], ["API Schema", "Ada", "Done"]]}}` (add/remove rows/columns via `board.tableEdit`).
  - Place reaction stamps (`"thumbsUp" | "heart" | "plusOne" | "star" | "question" | "check"`): `board.stamp {x: 200, y: 150, stamp: "thumbsUp"}`.
  - Freehand marker or highlighter stroke: `board.ink {path: "M0 0 L120 0", highlighter: true, color: "yellow"}`.
  - Customize board background grid (`"dots" | "lines" | "graph" | "none"`): `board.grid {style: "dots", spacing: 24}`.

### Running Workshop Timers & Dot-Voting Sessions

- **Countdown Timer (`board.timer` / `board.timerState`)**:
  - `board.timer {action: "start", minutes: 5}`, `board.timer {action: "add", minutes: 2}`, `board.timer {action: "pause"}`, `board.timer {action: "resume"}`, `board.timer {action: "stop"}`.
- **Dot Voting (`board.vote` / `board.voteResults`)**:
  1. Start a voting round: `run_command {command: "board.vote", params: {action: "start", votes: 3, on: "stickies"}}`
  2. Cast or retract votes: `run_command {command: "board.vote", params: {action: "cast", id: stickyId}}`
  3. End session & rank results (most votes first): `run_command {command: "board.vote", params: {action: "end"}}`
  4. Read ranked tally: `run_command {command: "board.voteResults"}`.

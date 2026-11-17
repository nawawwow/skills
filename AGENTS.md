# AGENTS.md — Agent Skills Collection

Repository-specific operating instructions for AI coding agents working in the `skills` workspace. Inherits global rules from `~/.agents/AGENTS.md` (`Windows` / `PowerShell`), overriding or extending them for this repository where specified below.

## Project Overview & Tech Stack

- **Archetype:** AI Agent Skills Collection ([Agent Skills Standard](https://skills.sh))
- **OS & Shell:** Windows (`PowerShell`). Always use PowerShell-compatible syntax and quote URLs containing `&`.
- **Primary Stack:** Python 3.10+ (stdlib-first CLI utilities, PyYAML, JSON Schema), Node.js 18+ (`npx` tooling), Ruff, Mypy, Prettier, and Markdownlint.
- **Manifests:** `pyproject.toml`, `.skill-lock.json`, `.prettierrc.json`, `.markdownlint.json`.
- **Human Documentation:** Refer to `README.md` for architecture and `skills/<skill-name>/SKILL.md` for individual skill workflows.

## Language & Communication Policy

- **User Communication (Bahasa Indonesia):** Respond, explain, and summarize in **Bahasa Indonesia** (unless the user explicitly prompts in another language). Keep explanations concise, structured, and actionable.
- **Technical Artifacts (English):** Write all code identifiers, inline comments, docstrings, schemas, skill docs, Issue titles/descriptions/comments, Pull Request descriptions, and Git commit messages strictly in **English**.

## Operational Commands

### Setup & Build

- **Install dependencies:** `pip install -e .`
- **Build application:** No build required (zero-build Python package & documentation repository).

### Testing & Skill Validation (Single-Test First Rule)

Never execute full benchmark suites for isolated edits; validate targeted skills and single tests first:

- **Run single test (Python):** `pytest <path_to_test>::<test_name>`
- **Full test suite (pre-PR):** `pytest`
- **Validate a skill:** `python skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`
- **Deep validate a skill:** `python skills/skill-creator/scripts/validate_skill.py skills/<skill-name>`

### Lint, Typecheck & DocOps Gates

- **Lint & format Python:** `ruff check .` and `ruff format --check .` (auto-format with `ruff format .`)
- **Type check Python:** `python -m mypy skills/<skill-name>/scripts` (run per skill directory to avoid cross-skill script name collisions)
- **Lint & format Markdown/JSON:** `npx markdownlint-cli2 "**/*.md"` and `npx prettier --end-of-line auto --check "**/*.md" "**/*.json"` (`--write` to format)
- **Audit commit & message:** `python skills/git-commit/scripts/prepare_commit.py --dry-run` and `python skills/git-commit/scripts/verify_commit_msg.py "<header>"`

## Code Style & Architectural Conventions

- Enforce strict Python 3.10+ type hints (`dict`, `list`, `X | None`); avoid untyped dictionaries or implicit `Any`.
- Handle errors explicitly with meaningful context; never swallow exceptions with empty or bare `except:` blocks.
- Preserve existing comments, docstrings, and formatting conventions in untouched code regions.
- **Progressive Disclosure:** Keep `SKILL.md` under 500 lines; offload deep reference material to `references/`, utilities to `scripts/`, and templates to `assets/` within one hop of `SKILL.md`.
- **Description Constraint:** Keep `SKILL.md` frontmatter `description` at most 1024 characters with clear trigger contexts.
- **Deterministic Scripts:** Write deterministic Python 3.10+ stdlib-first CLI scripts in `scripts/` with UTF-8 safe Windows console output (`sys.stdout.reconfigure(encoding="utf-8", errors="replace")`).

## Boundaries & "Never Do" Rules

- Never push directly to `main`, `master`, `staging`, or `production` branches.
- Never execute remote write or release operations—including `git push`, `git push --force-with-lease`, `git tag`, `gh release`, `gh pr create`, `gh pr merge`, `gh issue create`, `gh issue edit`, `gh issue comment`, `gh issue close`, or deleting remote branches—without **explicit user permission** (read-only queries like `gh issue list`/`view`, local branching, local commits, and local interactive rebases are permitted when requested).
- Never run raw `git push --force`, and never rewrite history on shared/public branches (`main`, `master`, `staging`, `production`, `dev`); on short-lived feature branches, use `git push --force-with-lease` (with explicit user permission) after a local rebase or fixup.
- Never stage or commit secrets, `.env` files, API keys, credentials, or private tokens; audit `git diff --cached` and run `prepare_commit.py --dry-run` before every commit.
- Never manually edit internal agent directories, generated outputs, or lockfiles (`.gemini/`, `.git/`, `.agent-archive/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.venv/`, `node_modules/`, `package-lock.json`, `pnpm-lock.yaml`, `uv.lock`).
- Never delete or rename existing skills without explicit user instruction.
- Never exceed the 1024-character limit for skill descriptions, create circular reference links, or leave unreplaced placeholder tokens in production files.
- Never bypass security checks, validation gates, or pre-commit hooks (`--no-verify`).

## PR & Git Guidelines

- **Issue Tracking (Pragmatic Issue-First):** Require a GitHub Issue (written in English with Problem/Context and Acceptance Criteria or Steps to Reproduce) for new features, bug fixes, and architectural changes before implementation; trivial changes (typos, minor docs, routine config updates) do not require an issue.
- **Branching & Syncing:** Branch short-lived work from `dev` or an up-to-date `main` using `<prefix>/<issue-number>-<short-slug>` when an issue exists (or `<prefix>/<short-slug>` for issue-less trivial changes; prefixes: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`), syncing locally via `git fetch origin` and `git rebase` before merging.
- **Atomic & Conventional Commits (1.0.0):** Use `<type>(<scope>): <imperative lowercase summary>` (max 72 chars), scoped atomically without repeating the issue number in every commit; absorb minor fixes or review revisions via `git commit --amend` or `--fixup` + `git rebase -i --autosquash` rather than stacking noisy fixup commits.
- **Pull Request & Merge Strategy:** Target small reviewable PRs (under 300–400 changed lines) with a clear summary, linked closing issue (`Closes #42`) when applicable, and verification output; merge using **Semi-linear Merge** (`--merge` after rebase, preserving every atomic commit—never squash-merge multi-commit branches), keeping `dev -> main` aligned.
- **Pre-PR Quality Gates:** Run `ruff check .`, `ruff format --check .`, `python -m mypy skills/<skill-name>/scripts`, `npx markdownlint-cli2 "**/*.md"`, `npx prettier --end-of-line auto --check "**/*.md" "**/*.json"`, and `validate_skill.py` on affected skills before presenting diffs or opening a PR.

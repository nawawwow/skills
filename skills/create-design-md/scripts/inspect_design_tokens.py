#!/usr/bin/env python3
"""
inspect_design_tokens.py - Static design token and styling inspector for create-design-md.

Scans a project directory to discover existing design tokens, CSS custom properties,
Tailwind v3/v4 configurations, W3C DTCG token files, UI libraries, font stacks, and
existing DESIGN.md files to bootstrap or audit a DESIGN.md specification.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "out",
    "target",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".gemini",
    ".agent-archive",
}


def find_files(root: Path, patterns: list[str], max_depth: int = 3) -> list[Path]:
    """Find files matching glob patterns within max_depth, skipping ignored directories."""
    results: list[Path] = []
    for pattern in patterns:
        for path in root.rglob(pattern):
            try:
                rel_parts = path.relative_to(root).parts
                if len(rel_parts) > max_depth:
                    continue
                if any(part in IGNORED_DIRS for part in rel_parts):
                    continue
                if path.is_file() and path not in results:
                    results.append(path)
            except ValueError:
                continue
    return sorted(results)


def inspect_package_json(root: Path) -> dict[str, Any]:
    """Extract project name, UI libraries, and font packages from package.json."""
    pkg_file = root / "package.json"
    info: dict[str, Any] = {
        "name": root.name,
        "description": "",
        "ui_libraries": [],
        "fonts": [],
        "has_google_design_md_cli": False,
    }
    if not pkg_file.exists():
        return info

    try:
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        info["name"] = data.get("name") or root.name
        info["description"] = data.get("description") or ""
        deps: dict[str, str] = {}
        deps.update(data.get("dependencies") or {})
        deps.update(data.get("devDependencies") or {})

        ui_Indicators = [
            "tailwindcss",
            "@tailwindcss/vite",
            "@tailwindcss/postcss",
            "shadcn-ui",
            "@radix-ui/react-slot",
            "@mui/material",
            "@chakra-ui/react",
            "antd",
            "lucide-react",
            "framer-motion",
            "class-variance-authority",
        ]
        for lib in ui_Indicators:
            if lib in deps:
                info["ui_libraries"].append(lib)

        for dep_name in deps:
            if dep_name.startswith("@fontsource/"):
                font_slug = dep_name.split("/", 1)[1].replace("-", " ").title()
                info["fonts"].append(font_slug)

        if "@google/design.md" in deps:
            info["has_google_design_md_cli"] = True
    except Exception:
        pass

    return info


def extract_css_tokens(root: Path) -> dict[str, dict[str, str]]:
    """Extract CSS custom properties and Tailwind v4 @theme tokens from stylesheets."""
    css_files = find_files(root, ["*.css"], max_depth=4)
    colors: dict[str, str] = {}
    fonts: dict[str, str] = {}
    radii: dict[str, str] = {}
    spacing: dict[str, str] = {}

    var_pattern = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;\}]+);")
    for css_file in css_files:
        try:
            content = css_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for match in var_pattern.finditer(content):
            key, raw_val = match.group(1).strip(), match.group(2).strip()
            if key.startswith("color-"):
                token_name = key[len("color-") :]
                colors[token_name] = raw_val
            elif key in {
                "primary",
                "secondary",
                "tertiary",
                "neutral",
                "surface",
                "background",
                "foreground",
                "accent",
                "muted",
                "error",
                "destructive",
            }:
                if re.match(r"^(#|rgb|hsl|oklch|color-mix)", raw_val, re.I):
                    colors[key] = raw_val
            elif key.startswith("font-"):
                fonts[key[len("font-") :]] = raw_val.strip("\"'")
            elif key.startswith("radius"):
                r_key = key[len("radius-") :] if key.startswith("radius-") else "md"
                radii[r_key] = raw_val
            elif key.startswith("spacing-"):
                spacing[key[len("spacing-") :]] = raw_val

    return {
        "colors": colors,
        "fonts": fonts,
        "rounded": radii,
        "spacing": spacing,
    }


def extract_dtcg_tokens(root: Path) -> dict[str, dict[str, Any]]:
    """Extract tokens from W3C DTCG / tokens.json files if present."""
    token_files = find_files(
        root,
        ["tokens.json", "design_tokens.json", "design-tokens.json", "*.tokens.json"],
        max_depth=3,
    )
    extracted: dict[str, dict[str, Any]] = {
        "colors": {},
        "typography": {},
        "rounded": {},
        "spacing": {},
    }
    for tf in token_files:
        try:
            data = json.loads(tf.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue

        color_group = data.get("color") or data.get("colors") or {}
        if isinstance(color_group, dict):
            for k, v in color_group.items():
                if isinstance(v, dict) and ("$value" in v or "value" in v):
                    extracted["colors"][k] = str(v.get("$value") or v.get("value"))
                elif isinstance(v, str):
                    extracted["colors"][k] = v

        radius_group = data.get("rounded") or data.get("borderRadius") or data.get("radius") or {}
        if isinstance(radius_group, dict):
            for k, v in radius_group.items():
                if isinstance(v, dict) and ("$value" in v or "value" in v):
                    extracted["rounded"][k] = str(v.get("$value") or v.get("value"))
                elif isinstance(v, str):
                    extracted["rounded"][k] = v

        space_group = data.get("spacing") or data.get("space") or {}
        if isinstance(space_group, dict):
            for k, v in space_group.items():
                if isinstance(v, dict) and ("$value" in v or "value" in v):
                    extracted["spacing"][k] = str(v.get("$value") or v.get("value"))
                elif isinstance(v, (str, int, float)):
                    extracted["spacing"][k] = str(v)

    return extracted


def inspect_existing_design_md(root: Path) -> dict[str, Any]:
    """Check if DESIGN.md already exists and classify its structure."""
    design_md = root / "DESIGN.md"
    if not design_md.exists():
        return {"exists": False, "mode": "none", "sections": []}

    content = design_md.read_text(encoding="utf-8", errors="replace")
    has_frontmatter = content.startswith("---\n") or content.startswith("---\r\n")
    has_yaml_blocks = bool(re.search(r"^```yaml\b", content, re.M))
    headings = re.findall(r"^##\s+(.+)$", content, re.M)

    if has_frontmatter and has_yaml_blocks:
        mode = "hybrid-interleaved"
    elif has_frontmatter:
        mode = "frontmatter"
    elif has_yaml_blocks:
        mode = "interleaved"
    else:
        mode = "prose-only"

    return {
        "exists": True,
        "path": str(design_md),
        "mode": mode,
        "sections": [h.strip() for h in headings],
        "line_count": len(content.splitlines()),
    }


def recommend_archetype(
    pkg_info: dict[str, Any],
    css_tokens: dict[str, dict[str, str]],
) -> str:
    """Recommend one of the 6 DESIGN.md archetypes based on project signals."""
    colors = css_tokens.get("colors", {})
    bg = colors.get("background") or colors.get("surface") or ""
    if bg.startswith("#0") or bg.startswith("#1"):
        return "atmospheric-minimal"
    if any(lib in pkg_info.get("ui_libraries", []) for lib in ["@mui/material", "antd"]):
        return "enterprise-clarity"
    return "editorial-prestige"


def inspect_project_design(project_dir: str = ".") -> dict[str, Any]:
    """Perform full static discovery of design tokens and UI metadata."""
    root = Path(project_dir).resolve()
    pkg_info = inspect_package_json(root)
    css_tokens = extract_css_tokens(root)
    dtcg_tokens = extract_dtcg_tokens(root)
    existing_design = inspect_existing_design_md(root)

    merged_colors: dict[str, str] = {}
    merged_colors.update(dtcg_tokens["colors"])
    merged_colors.update(css_tokens["colors"])

    merged_rounded: dict[str, str] = {}
    merged_rounded.update(dtcg_tokens["rounded"])
    merged_rounded.update(css_tokens["rounded"])

    merged_spacing: dict[str, str] = {}
    merged_spacing.update(dtcg_tokens["spacing"])
    merged_spacing.update(css_tokens["spacing"])

    archetype = recommend_archetype(pkg_info, {"colors": merged_colors})

    return {
        "project_name": pkg_info["name"],
        "description": pkg_info["description"],
        "ui_libraries": pkg_info["ui_libraries"],
        "discovered_fonts": pkg_info["fonts"] or list(css_tokens["fonts"].values()),
        "has_google_design_md_cli": pkg_info["has_google_design_md_cli"],
        "existing_design_md": existing_design,
        "discovered_tokens": {
            "colors": merged_colors,
            "rounded": merged_rounded,
            "spacing": merged_spacing,
        },
        "recommended_archetype": archetype,
    }


def format_summary(data: dict[str, Any]) -> str:
    """Format inspection report as human-readable CLI output."""
    lines = [
        "=" * 72,
        f" DESIGN.md TOKEN & STYLING INSPECTION: {data['project_name']}",
        "=" * 72,
        f" Recommended Archetype : {data['recommended_archetype']}",
        f" UI Libraries Detected : {', '.join(data['ui_libraries']) or 'None detected'}",
        f" Fonts Detected        : {', '.join(data['discovered_fonts']) or 'None detected'}",
        f" @google/design.md CLI : {'Installed' if data['has_google_design_md_cli'] else 'Not in package.json (use npx -p @google/design.md designmd)'}",
    ]
    existing = data["existing_design_md"]
    if existing["exists"]:
        lines.append(
            f" Existing DESIGN.md    : Yes ({existing['mode']}, {existing['line_count']} lines, {len(existing['sections'])} sections)"
        )
    else:
        lines.append(" Existing DESIGN.md    : None")

    tokens = data["discovered_tokens"]
    lines.append(
        f" Discovered Tokens     : {len(tokens['colors'])} colors, {len(tokens['rounded'])} radii, {len(tokens['spacing'])} spacing"
    )
    lines.append("=" * 72)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect codebase for existing design tokens, CSS variables, and DESIGN.md state."
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Path to the target project directory (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output inspection data as structured JSON.",
    )
    args = parser.parse_args()

    data = inspect_project_design(args.project_dir)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_summary(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())

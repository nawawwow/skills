#!/usr/bin/env python3
"""
export_design_md.py - Token compiler, exporter, and version differ for DESIGN.md.

Compiles DESIGN.md tokens (resolving {path.to.token} references) into:
- json-tailwind / tailwind : Tailwind CSS v3 theme.extend JSON object
- css-tailwind             : Tailwind CSS v4 @theme { ... } CSS custom properties block
- dtcg                     : W3C Design Tokens Format Module (tokens.json)
Also supports comparing two DESIGN.md files (--diff) to detect token and lint regressions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from audit_design_md import (
        extract_yaml_and_sections,
        resolve_token_ref,
        run_linter_and_rubric,
    )
except ImportError:
    import importlib

    _mod = importlib.import_module("scripts.audit_design_md")
    extract_yaml_and_sections = _mod.extract_yaml_and_sections
    resolve_token_ref = _mod.resolve_token_ref
    run_linter_and_rubric = _mod.run_linter_and_rubric


def resolve_all_tokens(tokens: dict[str, Any]) -> dict[str, Any]:
    """Resolve all {path.to.token} references in colors, rounded, spacing, and typography."""
    resolved: dict[str, Any] = {}
    for group in ("colors", "rounded", "spacing"):
        raw_group = tokens.get(group)
        if isinstance(raw_group, dict):
            resolved[group] = {}
            for k, v in raw_group.items():
                val, err = resolve_token_ref(v, tokens)
                resolved[group][k] = val if not err and val is not None else v

    raw_typo = tokens.get("typography")
    if isinstance(raw_typo, dict):
        resolved["typography"] = {}
        for t_name, t_props in raw_typo.items():
            if isinstance(t_props, dict):
                resolved["typography"][t_name] = dict(t_props)
    return resolved


def export_json_tailwind(tokens: dict[str, Any]) -> str:
    """Export tokens as Tailwind v3 theme.extend JSON config."""
    res = resolve_all_tokens(tokens)
    font_families: dict[str, list[str]] = {}
    font_sizes: dict[str, Any] = {}

    for t_name, t_props in res.get("typography", {}).items():
        if isinstance(t_props, dict):
            ff = t_props.get("fontFamily")
            if ff:
                slug = str(ff).lower().replace(" ", "-")
                font_families[slug] = [str(ff), "sans-serif"]
            fs = t_props.get("fontSize")
            if fs:
                meta: dict[str, Any] = {}
                for prop_k in ("lineHeight", "letterSpacing", "fontWeight"):
                    if prop_k in t_props:
                        meta[prop_k] = str(t_props[prop_k])
                font_sizes[t_name] = [str(fs), meta] if meta else str(fs)

    payload = {
        "theme": {
            "extend": {
                "colors": res.get("colors", {}),
                "fontFamily": font_families,
                "fontSize": font_sizes,
                "borderRadius": res.get("rounded", {}),
                "spacing": res.get("spacing", {}),
            }
        }
    }
    return json.dumps(payload, indent=2)


def export_css_tailwind(tokens: dict[str, Any]) -> str:
    """Export tokens as a Tailwind v4 @theme CSS block."""
    res = resolve_all_tokens(tokens)
    lines = ["@theme {"]

    colors = res.get("colors", {})
    if colors:
        lines.append("  /* Colors */")
        for k, v in colors.items():
            lines.append(f"  --color-{k}: {v};")

    typo = res.get("typography", {})
    if typo:
        lines.append("")
        lines.append("  /* Typography */")
        seen_fonts: set[str] = set()
        for t_name, t_props in typo.items():
            if not isinstance(t_props, dict):
                continue
            ff = t_props.get("fontFamily")
            if ff and str(ff) not in seen_fonts:
                seen_fonts.add(str(ff))
                slug = str(ff).lower().replace(" ", "-")
                lines.append(f'  --font-{slug}: "{ff}", sans-serif;')
            if "fontSize" in t_props:
                lines.append(f"  --text-{t_name}: {t_props['fontSize']};")
            if "lineHeight" in t_props:
                lines.append(f"  --leading-{t_name}: {t_props['lineHeight']};")
            if "letterSpacing" in t_props:
                lines.append(f"  --tracking-{t_name}: {t_props['letterSpacing']};")
            if "fontWeight" in t_props:
                lines.append(f"  --font-weight-{t_name}: {t_props['fontWeight']};")

    rounded = res.get("rounded", {})
    if rounded:
        lines.append("")
        lines.append("  /* Border Radius */")
        for k, v in rounded.items():
            lines.append(f"  --radius-{k}: {v};")

    spacing = res.get("spacing", {})
    if spacing:
        lines.append("")
        lines.append("  /* Spacing */")
        for k, v in spacing.items():
            lines.append(f"  --spacing-{k}: {v};")

    lines.append("}")
    return "\n".join(lines)


def export_dtcg(tokens: dict[str, Any]) -> str:
    """Export tokens as W3C Design Tokens Format Module (DTCG) JSON."""
    res = resolve_all_tokens(tokens)
    dtcg: dict[str, Any] = {
        "color": {},
        "typography": {},
        "rounded": {},
        "spacing": {},
    }
    for k, v in res.get("colors", {}).items():
        dtcg["color"][k] = {"$type": "color", "$value": str(v)}
    for k, v in res.get(" typography", res.get("typography", {})).items():
        dtcg["typography"][k] = {"$type": "typography", "$value": v}
    for k, v in res.get("rounded", {}).items():
        dtcg["rounded"][k] = {"$type": "dimension", "$value": str(v)}
    for k, v in res.get("spacing", {}).items():
        dtcg["spacing"][k] = {"$type": "dimension", "$value": str(v)}
    return json.dumps(dtcg, indent=2)


def diff_design_md(before_text: str, after_text: str) -> tuple[dict[str, Any], int]:
    """Compare two DESIGN.md contents and report token deltas and lint regressions."""
    rep_before = run_linter_and_rubric(before_text)
    rep_after = run_linter_and_rubric(after_text)

    tok_before = rep_before["tokens"]
    tok_after = rep_after["tokens"]

    token_deltas: dict[str, dict[str, list[str]]] = {}
    for cat in ("colors", "typography", "rounded", "spacing", "components"):
        b_map = tok_before.get(cat) if isinstance(tok_before.get(cat), dict) else {}
        a_map = tok_after.get(cat) if isinstance(tok_after.get(cat), dict) else {}
        b_keys = set(b_map.keys())
        a_keys = set(a_map.keys())
        added = sorted(a_keys - b_keys)
        removed = sorted(b_keys - a_keys)
        modified = sorted(k for k in (a_keys & b_keys) if b_map[k] != a_map[k])
        token_deltas[cat] = {
            "added": added,
            "removed": removed,
            "modified": modified,
        }

    sum_b = rep_before["summary"]
    sum_a = rep_after["summary"]
    err_delta = int(sum_a["errors"]) - int(sum_b["errors"])
    warn_delta = int(sum_a["warnings"]) - int(sum_b["warnings"])
    regression = err_delta > 0 or warn_delta > 0

    result = {
        "tokens": token_deltas,
        "findings": {
            "before": sum_b,
            "after": sum_a,
            "delta": {"errors": err_delta, "warnings": warn_delta},
        },
        "regression": regression,
    }
    return result, (1 if regression else 0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export DESIGN.md tokens to Tailwind v3/v4 or W3C DTCG, or diff two DESIGN.md files."
    )
    parser.add_argument(
        "file",
        help="Path to the source DESIGN.md file.",
    )
    parser.add_argument(
        "--format",
        choices=["json-tailwind", "tailwind", "css-tailwind", "dtcg"],
        default="css-tailwind",
        help="Export target format (default: css-tailwind).",
    )
    parser.add_argument(
        "--diff",
        type=Path,
        default=None,
        help="Compare 'file' (before) against this second DESIGN.md file (after).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="-",
        help="Output file path (default: '-' for stdout).",
    )
    args = parser.parse_args()

    src_path = Path(args.file)
    if not src_path.exists():
        print(f"Error: Input file cannot be read: {src_path}", file=sys.stderr)
        return 2

    src_text = src_path.read_text(encoding="utf-8", errors="replace")

    if args.diff is not None:
        if not args.diff.exists():
            print(f"Error: Diff target file cannot be read: {args.diff}", file=sys.stderr)
            return 2
        after_text = args.diff.read_text(encoding="utf-8", errors="replace")
        diff_report, exit_code = diff_design_md(src_text, after_text)
        output_str = json.dumps(diff_report, indent=2)
        if args.output == "-":
            print(output_str)
        else:
            Path(args.output).write_text(output_str, encoding="utf-8")
        return exit_code

    tokens, _headings, _findings = extract_yaml_and_sections(src_text)
    if args.format in ("json-tailwind", "tailwind"):
        output_str = export_json_tailwind(tokens)
    elif args.format == "css-tailwind":
        output_str = export_css_tailwind(tokens)
    else:
        output_str = export_dtcg(tokens)

    if args.output == "-":
        print(output_str)
    else:
        Path(args.output).write_text(output_str, encoding="utf-8")
        print(f"Exported {args.format} tokens -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

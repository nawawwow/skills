#!/usr/bin/env python3
"""
audit_design_md.py - Linter and 12-Point Quality Auditor for DESIGN.md.

Implements all 11 official @google/design.md linter rules (broken-ref, missing-primary,
contrast-ratio WCAG AA 4.5:1, orphaned-tokens, token-summary, missing-sections,
missing-typography, section-order, unknown-key Levenshtein check, token-like-ignored,
omitted-rules) plus a 100-point quality rubric enforcing an 80/100 passing gate.
"""

from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

KNOWN_TOP_KEYS = {
    "version",
    "name",
    "description",
    "omitted",
    "colors",
    "typography",
    "rounded",
    "spacing",
    "components",
}

CANONICAL_SECTIONS: list[tuple[str, set[str]]] = [
    ("Overview", {"overview", "brand & style", "visual theme & atmosphere"}),
    ("Colors", {"colors", "color palette & roles"}),
    ("Typography", {"typography", "typography rules"}),
    ("Layout", {"layout", "layout & spacing", "layout principles"}),
    ("Elevation & Depth", {"elevation & depth", "elevation", "depth & elevation"}),
    ("Shapes", {"shapes", "rounded corners"}),
    ("Components", {"components", "component stylings", "component patterns"}),
    ("Do's and Don'ts", {"do's and don'ts", "dos and donts", "constraints"}),
]

AI_SLOP_BUZZWORDS = [
    r"\bmodern,\s*clean\b",
    r"\bclean\s+and\s+modern\b",
    r"\btrustworthy\s+and\s+premium\b",
    r"\bcutting-edge\b",
    r"\bnext-gen\b",
]


def levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        return levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            ins = prev[j + 1] + 1
            dele = curr[j] + 1
            sub = prev[j] + (0 if ca == cb else 1)
            curr.append(min(ins, dele, sub))
        prev = curr
    return prev[-1]


def parse_simple_yaml(yaml_text: str) -> dict[str, Any]:
    """Parse YAML block using PyYAML if available, with stdlib indentation fallback."""
    try:
        import yaml

        loaded = yaml.safe_load(yaml_text)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        pass

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in yaml_text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().strip("\"'")
        val = val.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if not val:
            new_map: dict[str, Any] = {}
            parent[key] = new_map
            stack.append((indent, new_map))
        else:
            clean_val: Any = val.strip("\"'")
            if clean_val.isdigit():
                clean_val = int(clean_val)
            parent[key] = clean_val
    return root


def extract_yaml_and_sections(
    content: str,
) -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
    """Extract merged YAML token tree, duplicate key errors, and markdown ## sections."""
    findings: list[dict[str, Any]] = []
    yaml_blocks: list[str] = []

    fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", content, re.S)
    body = content
    if fm_match:
        yaml_blocks.append(fm_match.group(1))
        body = content[fm_match.end() :]

    for block_match in re.finditer(r"^```ya?ml\s*\r?\n(.*?)\r?\n```", body, re.M | re.S):
        yaml_blocks.append(block_match.group(1))

    merged_tokens: dict[str, Any] = {}
    seen_top_keys: set[str] = set()
    for block in yaml_blocks:
        parsed = parse_simple_yaml(block)
        for k, v in parsed.items():
            if k in seen_top_keys:
                findings.append(
                    {
                        "rule": "duplicate-top-key",
                        "severity": "error",
                        "path": k,
                        "message": f"Duplicate top-level YAML key '{k}' defined across multiple blocks.",
                    }
                )
            seen_top_keys.add(k)
            merged_tokens[k] = v

    headings = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", body, re.M)]
    return merged_tokens, headings, findings


def resolve_token_ref(
    value: Any,
    token_tree: dict[str, Any],
    max_depth: int = 10,
) -> tuple[Any, str | None]:
    """Resolve {path.to.token} references up to max_depth."""
    curr = value
    depth = 0
    while isinstance(curr, str) and curr.startswith("{") and curr.endswith("}"):
        if depth >= max_depth:
            return None, f"Token reference '{value}' exceeded max reference depth ({max_depth})."
        ref_path = curr[1:-1].strip().split(".")
        node: Any = token_tree
        for part in ref_path:
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return None, f"Token reference '{curr}' does not resolve to any defined token."
        curr = node
        depth += 1
    return curr, None


def parse_css_color_to_rgb(color_str: str) -> tuple[float, float, float] | None:
    """Parse hex (#RGB, #RRGGBB), rgb(), rgba(), or hsl() into normalized sRGB (0..1)."""
    s = color_str.strip().lower()
    if s.startswith("#"):
        hex_part = s[1:]
        if len(hex_part) in (3, 4):
            r = int(hex_part[0] * 2, 16) / 255.0
            g = int(hex_part[1] * 2, 16) / 255.0
            b = int(hex_part[2] * 2, 16) / 255.0
            return (r, g, b)
        if len(hex_part) in (6, 8):
            r = int(hex_part[0:2], 16) / 255.0
            g = int(hex_part[2:4], 16) / 255.0
            b = int(hex_part[4:6], 16) / 255.0
            return (r, g, b)
    m_rgb = re.match(
        r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)",
        s,
    )
    if m_rgb:
        return (
            min(255.0, float(m_rgb.group(1))) / 255.0,
            min(255.0, float(m_rgb.group(2))) / 255.0,
            min(255.0, float(m_rgb.group(3))) / 255.0,
        )
    m_hsl = re.match(
        r"hsla?\(\s*([\d.]+)\s*,\s*([\d.]+)%?\s*,\s*([\d.]+)%?",
        s,
    )
    if m_hsl:
        h = (float(m_hsl.group(1)) % 360.0) / 360.0
        sat = max(0.0, min(100.0, float(m_hsl.group(2)))) / 100.0
        lig = max(0.0, min(100.0, float(m_hsl.group(3)))) / 100.0
        r, g, b = colorsys.hls_to_rgb(h, lig, sat)
        return (r, g, b)
    return None


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    """Compute WCAG 2.x relative luminance."""
    channels = []
    for c in rgb:
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(c1: tuple[float, float, float], c2: tuple[float, float, float]) -> float:
    """Compute WCAG contrast ratio between two sRGB colors."""
    l1 = relative_luminance(c1)
    l2 = relative_luminance(c2)
    bright, dark = (l1, l2) if l1 >= l2 else (l2, l1)
    return (bright + 0.05) / (dark + 0.05)


def run_linter_and_rubric(content: str) -> dict[str, Any]:
    """Run the 11 official @google/design.md linter rules and 12-point quality rubric."""
    tokens, headings, findings = extract_yaml_and_sections(content)

    # 1. unknown-key & token-like-ignored
    for k, v in tokens.items():
        if k not in KNOWN_TOP_KEYS:
            closest = min(KNOWN_TOP_KEYS, key=lambda kn: levenshtein(k.lower(), kn))
            if levenshtein(k.lower(), closest) <= 2:
                findings.append(
                    {
                        "rule": "unknown-key",
                        "severity": "warning",
                        "path": k,
                        "message": f"Top-level key '{k}' looks like a typo of '{closest}'.",
                    }
                )
            elif isinstance(v, dict) and any(
                isinstance(sv, str) and (sv.startswith("#") or sv.endswith(("px", "rem", "em")))
                for sv in v.values()
            ):
                findings.append(
                    {
                        "rule": "token-like-ignored",
                        "severity": "warning",
                        "path": k,
                        "message": f"Unknown top-level key '{k}' contains token-like values that will be ignored.",
                    }
                )

    # 2. omitted-rules
    omitted_raw = tokens.get("omitted") or []
    omitted_sections: set[str] = set()
    if isinstance(omitted_raw, list):
        for item in omitted_raw:
            if isinstance(item, str):
                omitted_sections.add(item.lower())
            elif isinstance(item, dict) and "section" in item:
                omitted_sections.add(str(item["section"]).lower())
        findings.append(
            {
                "rule": "omitted-rules",
                "severity": "info",
                "path": "omitted",
                "message": f"Intentionally omitted sections configured: {sorted(omitted_sections)}",
            }
        )

    colors: dict[str, Any] = tokens["colors"] if isinstance(tokens.get("colors"), dict) else {}
    typography: dict[str, Any] = (
        tokens["typography"] if isinstance(tokens.get("typography"), dict) else {}
    )
    rounded: dict[str, Any] = tokens["rounded"] if isinstance(tokens.get("rounded"), dict) else {}
    spacing: dict[str, Any] = tokens["spacing"] if isinstance(tokens.get("spacing"), dict) else {}
    components: dict[str, Any] = (
        tokens["components"] if isinstance(tokens.get("components"), dict) else {}
    )

    # 3. missing-primary & missing-typography & missing-sections
    if colors and "primary" not in colors:
        findings.append(
            {
                "rule": "missing-primary",
                "severity": "warning",
                "path": "colors",
                "message": "Colors are defined but no 'primary' color token exists.",
            }
        )
    if colors and not typography and "typography" not in omitted_sections:
        findings.append(
            {
                "rule": "missing-typography",
                "severity": "warning",
                "path": "typography",
                "message": "Colors are defined but no typography tokens exist.",
            }
        )

    missing_opt = [
        sec
        for sec, data in [("spacing", spacing), ("rounded", rounded), ("components", components)]
        if not data and sec not in omitted_sections
    ]
    if missing_opt:
        findings.append(
            {
                "rule": "missing-sections",
                "severity": "info",
                "path": ",".join(missing_opt),
                "message": f"Optional token groups absent: {', '.join(missing_opt)}.",
            }
        )

    # 4. broken-ref, contrast-ratio, orphaned-tokens
    referenced_colors: set[str] = set()
    for m_ref in re.finditer(r"\{colors\.([A-Za-z0-9_-]+)\}", content):
        referenced_colors.add(m_ref.group(1))

    broken_refs = 0
    contrast_failures = 0

    for comp_name, comp_props in components.items():
        if not isinstance(comp_props, dict):
            continue
        for prop_k, prop_v in comp_props.items():
            if isinstance(prop_v, str) and prop_v.startswith("{") and prop_v.endswith("}"):
                _, err = resolve_token_ref(prop_v, tokens)
                if err:
                    broken_refs += 1
                    findings.append(
                        {
                            "rule": "broken-ref",
                            "severity": "error",
                            "path": f"components.{comp_name}.{prop_k}",
                            "message": err,
                        }
                    )

        bg_raw = comp_props.get("backgroundColor")
        fg_raw = comp_props.get("textColor")
        if bg_raw and fg_raw:
            bg_val, err1 = resolve_token_ref(bg_raw, tokens)
            fg_val, err2 = resolve_token_ref(fg_raw, tokens)
            if not err1 and not err2 and isinstance(bg_val, str) and isinstance(fg_val, str):
                rgb_bg = parse_css_color_to_rgb(bg_val)
                rgb_fg = parse_css_color_to_rgb(fg_val)
                if rgb_bg and rgb_fg:
                    ratio = contrast_ratio(rgb_bg, rgb_fg)
                    if ratio < 4.5:
                        contrast_failures += 1
                        findings.append(
                            {
                                "rule": "contrast-ratio",
                                "severity": "warning",
                                "path": f"components.{comp_name}",
                                "message": (
                                    f"textColor ({fg_val}) on backgroundColor ({bg_val}) "
                                    f"has contrast ratio {ratio:.2f}:1 — below WCAG AA 4.5:1."
                                ),
                            }
                        )

    orphaned = [c_key for c_key in colors if c_key not in referenced_colors]
    if orphaned:
        findings.append(
            {
                "rule": "orphaned-tokens",
                "severity": "warning",
                "path": "colors",
                "message": f"Color tokens defined but never referenced: {', '.join(orphaned)}.",
            }
        )

    # 5. section-order & duplicate headings
    seen_headings: set[str] = set()
    matched_indices: list[int] = []
    for h in headings:
        h_low = h.lower().strip()
        if h_low in seen_headings:
            findings.append(
                {
                    "rule": "duplicate-section",
                    "severity": "error",
                    "path": f"## {h}",
                    "message": f"Duplicate section heading '## {h}' is not allowed.",
                }
            )
        seen_headings.add(h_low)
        for idx, (_canon_name, aliases) in enumerate(CANONICAL_SECTIONS):
            if h_low in aliases:
                matched_indices.append(idx)
                break

    if matched_indices != sorted(matched_indices):
        findings.append(
            {
                "rule": "section-order",
                "severity": "warning",
                "path": "sections",
                "message": "Markdown ## sections appear out of the canonical 1..8 specification order.",
            }
        )

    # 6. token-summary
    findings.append(
        {
            "rule": "token-summary",
            "severity": "info",
            "path": "root",
            "message": (
                f"Tokens defined: {len(colors)} colors, {len(typography)} typography, "
                f"{len(rounded)} rounded, {len(spacing)} spacing, {len(components)} components."
            ),
        }
    )

    # 12-Point Quality Rubric Calculation (100 points total)
    rubric: list[dict[str, Any]] = []

    def add_criterion(cid: str, name: str, weight: int, score: int, detail: str) -> None:
        status = "PASS" if score == weight else ("WARN" if score >= weight // 2 else "FAIL")
        rubric.append(
            {
                "id": cid,
                "name": name,
                "weight": weight,
                "score": score,
                "status": status,
                "detail": detail,
            }
        )

    has_dup_key = any(f["rule"] == "duplicate-top-key" for f in findings)
    s1 = 10 if (bool(tokens) and not has_dup_key) else 0
    add_criterion(
        "yaml_token_layer",
        "Valid YAML Token Layer & No Duplicate Keys",
        10,
        s1,
        "Normative YAML token tree parsed cleanly."
        if s1 == 10
        else "Missing or duplicate YAML token blocks.",
    )

    s2 = 8 if ("primary" in colors and len(colors) >= 4) else (4 if colors else 0)
    add_criterion(
        "color_palette",
        "Primary & Semantic Color Palette Completeness",
        8,
        s2,
        f"{len(colors)} color tokens defined including 'primary'."
        if s2 == 8
        else "Incomplete color token palette.",
    )

    s3 = 8 if len(typography) >= 3 else (4 if typography else 0)
    add_criterion(
        "typography_scale",
        "Typography Scale & Hierarchy Completeness",
        8,
        s3,
        f"{len(typography)} typography levels defined."
        if s3 == 8
        else "Fewer than 3 typography levels defined.",
    )

    s4 = 8 if (bool(spacing) and bool(rounded)) else (4 if (spacing or rounded) else 0)
    add_criterion(
        "spacing_and_shapes",
        "Spacing & Shape (rounded) Scales Defined",
        8,
        s4,
        f"{len(spacing)} spacing and {len(rounded)} rounded tokens defined.",
    )

    s5 = 8 if len(components) >= 3 else (4 if components else 0)
    add_criterion(
        "component_bindings",
        "Component Token Bindings & Variants",
        8,
        s5,
        f"{len(components)} component token definitions bound.",
    )

    s6 = 10 if broken_refs == 0 else 0
    add_criterion(
        "zero_broken_refs",
        "Zero Broken Token References ({path.to.token})",
        10,
        s6,
        "All {path.to.token} references resolve cleanly."
        if s6 == 10
        else f"{broken_refs} broken token reference(s).",
    )

    s7 = 10 if contrast_failures == 0 else max(0, 10 - contrast_failures * 5)
    add_criterion(
        "wcag_contrast",
        "WCAG AA Component Contrast Compliance (>= 4.5:1)",
        10,
        s7,
        "All component foreground/background pairs meet WCAG AA >= 4.5:1."
        if s7 == 10
        else f"{contrast_failures} component pair(s) failed WCAG AA 4.5:1.",
    )

    order_ok = matched_indices == sorted(matched_indices) and len(matched_indices) >= 6
    s8 = 8 if len(matched_indices) == 8 and order_ok else (5 if order_ok else 0)
    add_criterion(
        "canonical_sections",
        "Canonical 8-Section Prose Structure & Order",
        8,
        s8,
        f"{len(matched_indices)}/8 canonical sections present in valid order.",
    )

    slop_hits = [pat for pat in AI_SLOP_BUZZWORDS if re.search(pat, content, re.I)]
    s9 = 10 if not slop_hits and len(content.splitlines()) >= 40 else 4
    add_criterion(
        "specific_prose",
        "Specific Reference Prose & Anti-Slop Discipline",
        10,
        s9,
        "Evocative reference-driven prose with zero generic AI-slop clichés."
        if s9 == 10
        else "Generic buzzwords or thin prose detected.",
    )

    dont_count = len(re.findall(r"-\s+(?:\*\*)?Don't\b", content, re.I))
    do_count = len(re.findall(r"-\s+(?:\*\*)?Do\b", content, re.I))
    s10 = 8 if (dont_count >= 2 and do_count >= 2) else (4 if (dont_count + do_count >= 2) else 0)
    add_criterion(
        "negative_constraints",
        "Explicit Negative Constraints (Do's and Don'ts)",
        8,
        s10,
        f"{do_count} Do and {dont_count} Don't guardrails defined.",
    )

    s11 = 6 if not orphaned else max(0, 6 - len(orphaned) * 2)
    add_criterion(
        "zero_orphaned_tokens",
        "Token-to-Prose & Component Synchronization",
        6,
        s11,
        "Every color token is referenced in components or prose."
        if s11 == 6
        else f"Orphaned color tokens: {', '.join(orphaned)}",
    )

    placeholders = re.findall(r"\[TODO[^\]]*\]|FIXME|<your-[a-z-]+>|REPLACE_WITH_", content, re.I)
    s12 = 6 if not placeholders else 0
    add_criterion(
        "zero_placeholders",
        "Zero Unreplaced Placeholder Tokens",
        6,
        s12,
        "Zero placeholder tokens found." if s12 == 6 else f"Found placeholders: {placeholders[:3]}",
    )

    total_score = sum(int(r["score"]) for r in rubric)
    errors_count = sum(1 for f in findings if f["severity"] == "error")
    warnings_count = sum(1 for f in findings if f["severity"] == "warning")
    infos_count = sum(1 for f in findings if f["severity"] == "info")

    return {
        "total_score": total_score,
        "max_score": 100,
        "passed": total_score >= 80 and errors_count == 0,
        "summary": {
            "errors": errors_count,
            "warnings": warnings_count,
            "infos": infos_count,
        },
        "findings": findings,
        "rubric": rubric,
        "tokens": tokens,
    }


def format_report(report: dict[str, Any], target_file: str, min_score: int) -> str:
    """Format audit report as a readable CLI table."""
    s = report["summary"]
    passed = report["total_score"] >= min_score and s["errors"] == 0
    gate_str = f"PASSED GATE (>= {min_score}/100, 0 errors)" if passed else "FAILED GATE"
    lines = [
        f"DESIGN.md Quality & Spec Audit: {target_file}",
        "=" * 84,
        f"Total Quality Score : {report['total_score']} / {report['max_score']} ({gate_str})",
        f"Linter Summary      : {s['errors']} errors, {s['warnings']} warnings, {s['infos']} infos",
        "=" * 84,
        f"{'STATUS':<7} | {'SCORE':<7} | {'RUBRIC CRITERION':<44} | DETAILS",
        "-" * 84,
    ]
    for item in report["rubric"]:
        score_str = f"{item['score']}/{item['weight']}"
        lines.append(
            f"{item['status']:<7} | {score_str:<7} | {item['name']:<44} | {item['detail']}"
        )
    lines.append("=" * 84)

    non_info = [f for f in report["findings"] if f["severity"] in ("error", "warning")]
    if non_info:
        lines.append("\nLinter Findings:")
        for f in non_info:
            lines.append(f"  [{f['severity'].upper()}] ({f['rule']}) {f['path']}: {f['message']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit a DESIGN.md file against @google/design.md rules and the 12-point rubric."
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="DESIGN.md",
        help="Path to the DESIGN.md file to audit.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=80,
        help="Minimum passing score (default: 80).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON.",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        return 2

    content = path.read_text(encoding="utf-8", errors="replace")
    report = run_linter_and_rubric(content)
    if args.json:
        out_data = {k: v for k, v in report.items() if k != "tokens"}
        print(json.dumps(out_data, indent=2))
    else:
        print(format_report(report, str(path), args.min_score))

    if report["total_score"] < args.min_score or report["summary"]["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

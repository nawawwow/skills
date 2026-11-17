#!/usr/bin/env python3
"""
generate_design_md.py - Spec-compliant DESIGN.md generator for create-design-md.

Generates a dual-layer DESIGN.md (normative YAML design tokens + 8 canonical
Markdown prose sections) conforming to the Google Stitch / @google/design.md
specification across 6 archetypes, in either frontmatter or interleaved YAML mode.
Also supports converting pure-prose Stitch exports into hybrid token+prose files.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from inspect_design_tokens import inspect_project_design
except ImportError:
    import importlib

    inspect_project_design = importlib.import_module(
        "scripts.inspect_design_tokens"
    ).inspect_project_design


ARCHETYPES: dict[str, dict[str, Any]] = {
    "editorial-prestige": {
        "description": "Architectural minimalism and broadsheet editorial gravitas with high-contrast warm neutrals.",
        "overview": (
            "Architectural Minimalism meets Journalistic Gravitas. The interface evokes a "
            "1970s broadsheet monograph or contemporary gallery exhibition—built on warm limestone "
            "paper stock, deep graphite ink, and a single intentional terracotta accent.\n\n"
            "The UI avoids glossy gradients, neon drop shadows, and decorative chrome in favor of "
            "structural typography, hairline borders, and calm editorial authority."
        ),
        "colors": {
            "primary": "#1A1C1E",
            "on-primary": "#FFFFFF",
            "secondary": "#595F65",
            "on-secondary": "#FFFFFF",
            "tertiary": "#B8422E",
            "on-tertiary": "#FFFFFF",
            "neutral": "#F7F5F2",
            "surface": "#FFFFFF",
            "on-surface": "#1A1C1E",
            "outline": "#D4D0C8",
            "error": "#BA1A1A",
            "on-error": "#FFFFFF",
        },
        "colors_prose": [
            "**Primary (`{colors.primary}`) — Deep Broadsheet Ink**: Carries all primary headlines, body copy, and structural rules; never pure `#000000`.",
            "**Secondary (`{colors.secondary}`) — Archival Slate**: Used for captions, metadata, timestamps, and secondary navigation.",
            "**Tertiary (`{colors.tertiary}`) — Boston Clay**: The single interactive accent reserved strictly for primary call-to-actions and active indicators.",
            "**Neutral (`{colors.neutral}`) — Warm Limestone**: Page canvas foundation providing a tactile, glare-free reading surface.",
            "**Surface (`{colors.surface}`) — Gallery Card White**: Elevated card and sheet surface bounded by `{colors.outline}` hairline rules.",
            "**Error (`{colors.error}`) — Crimson Stamp**: Reserved for validation failures and destructive confirmations.",
        ],
        "typography": {
            "h1": {
                "fontFamily": "Public Sans",
                "fontSize": "48px",
                "fontWeight": 600,
                "lineHeight": 1.1,
                "letterSpacing": "-0.02em",
            },
            "h2": {
                "fontFamily": "Public Sans",
                "fontSize": "32px",
                "fontWeight": 600,
                "lineHeight": 1.2,
                "letterSpacing": "-0.01em",
            },
            "h3": {
                "fontFamily": "Public Sans",
                "fontSize": "22px",
                "fontWeight": 600,
                "lineHeight": 1.3,
            },
            "body-lg": {
                "fontFamily": "Public Sans",
                "fontSize": "18px",
                "fontWeight": 400,
                "lineHeight": 1.65,
            },
            "body-md": {
                "fontFamily": "Public Sans",
                "fontSize": "16px",
                "fontWeight": 400,
                "lineHeight": 1.6,
            },
            "label-caps": {
                "fontFamily": "Space Grotesk",
                "fontSize": "12px",
                "fontWeight": 500,
                "lineHeight": 1.0,
                "letterSpacing": "0.08em",
            },
        },
        "typography_prose": (
            "The typography system pairs **Public Sans** for institutional editorial clarity with "
            "**Space Grotesk** for technical metadata, numerals, and uppercase section labels.\n\n"
            "- **Headlines (`h1`–`h3`)**: Set in Public Sans Semi-Bold (`600`) with tight negative tracking (`-0.02em`) for authoritative hierarchy.\n"
            "- **Body (`body-lg`, `body-md`)**: Set at `16px`–`18px` with generous `1.6` line height for effortless long-form reading.\n"
            "- **Technical Labels (`label-caps`)**: Set in Space Grotesk (`12px`, `0.08em` tracking) for eyebrows, badges, and tabular figures."
        ),
        "spacing": {
            "xs": "4px",
            "sm": "8px",
            "md": "16px",
            "lg": "24px",
            "xl": "48px",
            "gutter": "24px",
            "margin": "32px",
        },
        "layout_prose": (
            "The layout follows a **12-column editorial grid** (max container width `1200px`, `{spacing.gutter}` gutters, "
            "`{spacing.margin}` outer margins) anchored to a strict `8px` spatial rhythm (`{spacing.xs}` half-step for optical alignment).\n\n"
            "Related content groups use structural containment inside `{colors.surface}` cards with `{spacing.lg}` internal padding "
            "and `1px solid` `{colors.outline}` dividers rather than floating shadow boxes."
        ),
        "elevation_prose": (
            "Hierarchy is communicated through **Tonal Layering and Hairline Rules** rather than heavy drop shadows. "
            "The `{colors.neutral}` canvas supports `{colors.surface}` containers separated by `1px` `{colors.outline}` borders. "
            "Modal dialogs use a single restrained shadow (`0 12px 32px rgba(26, 28, 30, 0.08)`)."
        ),
        "rounded": {
            "none": "0px",
            "sm": "4px",
            "md": "8px",
            "lg": "12px",
            "full": "9999px",
        },
        "shapes_prose": (
            "The geometry emphasizes **Architectural Sharpness**. Buttons and inputs use `{rounded.sm}` (`4px`), "
            "cards use `{rounded.md}` (`8px`), and status tags use `{rounded.full}` pills. Never mix large `24px` "
            "blobs with crisp `4px` controls in the same view."
        ),
        "components": {
            "button-primary": {
                "backgroundColor": "{colors.tertiary}",
                "textColor": "{colors.on-tertiary}",
                "typography": "{typography.label-caps}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
                "height": "44px",
            },
            "button-primary-hover": {
                "backgroundColor": "#963322",
                "textColor": "{colors.on-tertiary}",
            },
            "button-secondary": {
                "backgroundColor": "{colors.primary}",
                "textColor": "{colors.on-primary}",
                "typography": "{typography.label-caps}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
                "height": "44px",
            },
            "card-surface": {
                "backgroundColor": "{colors.surface}",
                "textColor": "{colors.on-surface}",
                "rounded": "{rounded.md}",
                "padding": "{spacing.lg}",
            },
            "input-field": {
                "backgroundColor": "{colors.neutral}",
                "textColor": "{colors.primary}",
                "typography": "{typography.body-md}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.sm}",
                "height": "44px",
            },
            "badge-muted": {
                "backgroundColor": "{colors.secondary}",
                "textColor": "{colors.on-secondary}",
                "typography": "{typography.label-caps}",
                "rounded": "{rounded.full}",
                "padding": "{spacing.xs}",
            },
            "alert-error": {
                "backgroundColor": "{colors.error}",
                "textColor": "{colors.on-error}",
                "typography": "{typography.body-md}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
            },
        },
        "components_prose": [
            "**Buttons (`button-primary`, `button-secondary`)**: Minimum `44px` touch target height, `{rounded.sm}` corners, and `{colors.tertiary}` fill for the single primary CTA per screen.",
            "**Cards (`card-surface`)**: Flat `{colors.surface}` background, `1px` `{colors.outline}` border, `{rounded.md}` radius, and `{spacing.lg}` padding.",
            "**Input Fields (`input-field`)**: `{colors.neutral}` fill, explicit visible label above the field, and `2px` `{colors.primary}` focus ring.",
            "**Badges & Alerts (`badge-muted`, `alert-error`)**: Pill badges in `{colors.secondary}` for metadata; `{colors.error}` banners for validation errors.",
        ],
        "dos_and_donts": [
            "**Do** reserve `{colors.tertiary}` exclusively for the single highest-priority interactive action on each view.",
            "**Do** maintain WCAG 2.2 AA contrast ratios (`>= 4.5:1` for body copy, `>= 3.0:1` for interactive boundaries).",
            "**Do** pair every color token with its semantic `on-*` foreground counterpart.",
            "**Don't** introduce neon purple-blue gradients, floating glowing orbs, or glassmorphism over `{colors.neutral}`.",
            "**Don't** use pure `#000000` black on pure `#FFFFFF` white; always anchor on `{colors.primary}` and `{colors.neutral}`.",
            "**Don't** mix more than two font families or exceed three font weights (`400`, `500`, `600`) on a single screen.",
        ],
    },
    "atmospheric-minimal": {
        "description": "High-craft dark UI with whisper-quiet luxury, 1px hairline borders, and monospace telemetry precision.",
        "overview": (
            "Precision Instrument Dark UI inspired by Linear, Raycast, and professional flight-deck telemetry. "
            "Deep obsidian surfaces (`{colors.neutral}`) frame crisp alabaster typography (`{colors.primary}`) "
            "and electric cobalt focus indicators (`{colors.tertiary}`).\n\n"
            "Every pixel serves speed and scannability: keyboard-first affordances, tabular numerals, "
            "and `1px` translucent borders replace heavy decoration."
        ),
        "colors": {
            "primary": "#F4F6FB",
            "on-primary": "#0B0F17",
            "secondary": "#94A3B8",
            "on-secondary": "#0B0F17",
            "tertiary": "#60A5FA",
            "on-tertiary": "#081226",
            "neutral": "#0B0F17",
            "surface": "#131A27",
            "on-surface": "#F4F6FB",
            "outline": "#263147",
            "error": "#F87171",
            "on-error": "#1F0909",
        },
        "colors_prose": [
            "**Primary (`{colors.primary}`) — Crisp Alabaster**: Primary foreground text and active iconography on dark surfaces.",
            "**Secondary (`{colors.secondary}`) — Muted Slate**: Secondary labels, keyboard shortcut hints (`⌘K`), and inactive tabs.",
            "**Tertiary (`{colors.tertiary}`) — Luminous Cobalt**: High-visibility accent for primary actions, focus rings, and active selection states.",
            "**Neutral (`{colors.neutral}`) — Obsidian Canvas**: Root application background.",
            "**Surface (`{colors.surface}`) — Elevated Slate Panel**: Cards, command palettes, and sidebars bounded by `{colors.outline}`.",
            "**Error (`{colors.error}`) — Coral Signal**: Destructive actions and error states with dark `{colors.on-error}` text.",
        ],
        "typography": {
            "h1": {
                "fontFamily": "Inter",
                "fontSize": "40px",
                "fontWeight": 600,
                "lineHeight": 1.15,
                "letterSpacing": "-0.025em",
            },
            "h2": {
                "fontFamily": "Inter",
                "fontSize": "28px",
                "fontWeight": 600,
                "lineHeight": 1.2,
                "letterSpacing": "-0.02em",
            },
            "body-md": {
                "fontFamily": "Inter",
                "fontSize": "14px",
                "fontWeight": 400,
                "lineHeight": 1.55,
            },
            "label-sm": {
                "fontFamily": "JetBrains Mono",
                "fontSize": "12px",
                "fontWeight": 500,
                "lineHeight": 1.2,
                "letterSpacing": "0.02em",
            },
        },
        "typography_prose": (
            "**Inter** handles UI copy and dense lists with `font-feature-settings: 'cv02', 'tnum'`, while "
            "**JetBrains Mono** renders commit SHAs, latency metrics, keybindings, and status badges."
        ),
        "spacing": {
            "xs": "4px",
            "sm": "8px",
            "md": "16px",
            "lg": "24px",
            "xl": "40px",
            "gutter": "16px",
            "margin": "24px",
        },
        "layout_prose": (
            "Compact workspace grid with `{spacing.gutter}` panel gaps, collapsible `240px` navigation rail, "
            "and `8px`/`4px` micro-spacing for high information density without visual clutter."
        ),
        "elevation_prose": (
            "Depth is established via **Luminance Stepping**: `{colors.neutral}` (`#0B0F17`) -> `{colors.surface}` (`#131A27`) "
            "with `1px solid` `{colors.outline}` top-edge highlights."
        ),
        "rounded": {
            "none": "0px",
            "sm": "6px",
            "md": "8px",
            "lg": "12px",
            "full": "9999px",
        },
        "shapes_prose": (
            "Tightly machined radii: `{rounded.sm}` (`6px`) for buttons and inputs, `{rounded.md}` (`8px`) for panels and command modals."
        ),
        "components": {
            "button-primary": {
                "backgroundColor": "{colors.tertiary}",
                "textColor": "{colors.on-tertiary}",
                "typography": "{typography.label-sm}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
                "height": "44px",
            },
            "button-secondary": {
                "backgroundColor": "{colors.primary}",
                "textColor": "{colors.on-primary}",
                "typography": "{typography.label-sm}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
                "height": "44px",
            },
            "card-surface": {
                "backgroundColor": "{colors.surface}",
                "textColor": "{colors.on-surface}",
                "rounded": "{rounded.md}",
                "padding": "{spacing.lg}",
            },
            "badge-muted": {
                "backgroundColor": "{colors.secondary}",
                "textColor": "{colors.on-secondary}",
                "typography": "{typography.label-sm}",
                "rounded": "{rounded.full}",
                "padding": "{spacing.xs}",
            },
            "alert-error": {
                "backgroundColor": "{colors.error}",
                "textColor": "{colors.on-error}",
                "typography": "{typography.body-md}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
            },
        },
        "components_prose": [
            "**Buttons (`button-primary`, `button-secondary`)**: Compact `{rounded.sm}` controls with `44px` hit target and crisp focus rings.",
            "**Surface Panels (`card-surface`)**: `{colors.surface}` fill with `1px` `{colors.outline}` border and zero heavy shadow.",
            "**Telemetry Badges (`badge-muted`, `alert-error`)**: Monospace `label-sm` pills with `{colors.secondary}` or `{colors.error}` fills.",
        ],
        "dos_and_donts": [
            "**Do** enable `tabular-nums` on all counters, timestamps, and table columns.",
            "**Do** use `1px` `{colors.outline}` borders to separate dark panes instead of heavy black drop shadows.",
            "**Don't** use saturated neon purple or rainbow gradients on dark backgrounds.",
            "**Don't** drop secondary text contrast below `4.5:1` against `{colors.surface}`.",
        ],
    },
}

# Populate remaining 4 archetypes concisely with complete WCAG-compliant token sets
for _arch_key, _arch_cfg in [
    (
        "enterprise-clarity",
        (
            "High-legibility B2B SaaS and analytics workspace engineered for dense tabular workflows.",
            "Swiss-grid enterprise workspace inspired by Stripe Dashboard and Bloomberg Terminal clarity. Prioritizes scannable data tables, unambiguous semantic status badges, and zero visual fatigue over multi-hour operator sessions.",
            "#0F172A",
            "#FFFFFF",
            "#475569",
            "#FFFFFF",
            "#1D4ED8",
            "#FFFFFF",
            "#F8FAFC",
            "#FFFFFF",
            "#0F172A",
            "#CBD5E1",
            "#B91C1C",
            "#FFFFFF",
            "Inter",
            "IBM Plex Mono",
        ),
    ),
    (
        "warm-organic",
        (
            "Tactile, human-centric consumer lifestyle and community design system with natural warmth.",
            "Warm botanical craft inspired by Aesop retail spaces and kinfolk print journals. Soft oat-milk surfaces (`{colors.neutral}`), deep espresso ink (`{colors.primary}`), and forest moss accents (`{colors.tertiary}`) create a calm, restorative digital environment.",
            "#231F1A",
            "#FFFFFF",
            "#61584E",
            "#FFFFFF",
            "#2D5A3C",
            "#FFFFFF",
            "#F6F2EA",
            "#FFFDF9",
            "#231F1A",
            "#DED6C8",
            "#A82424",
            "#FFFFFF",
            "Plus Jakarta Sans",
            "DM Mono",
        ),
    ),
    (
        "atmospheric-glass",
        (
            "Multi-layered translucent spatial UI with depth-aware luminance and crisp contrast.",
            "Atmospheric optical layering inspired by high-altitude meteorological instruments and spatial computing HUDs. Deep midnight sapphire surfaces (`{colors.neutral}`) pair with high-contrast ice typography (`{colors.primary}`) and sky-cyan interactive highlights (`{colors.tertiary}`).",
            "#F1F5F9",
            "#091122",
            "#93C5FD",
            "#091122",
            "#38BDF8",
            "#081526",
            "#091122",
            "#13203B",
            "#F1F5F9",
            "#2A3F66",
            "#FCA5A5",
            "#2A0707",
            "Inter",
            "Space Grotesk",
        ),
    ),
    (
        "technical-handout",
        (
            "Austere, information-dense academic specification and seminar handout system.",
            "A 1970s university computer science seminar handout and RFC specification sheet. Warm xerox stock (`{colors.neutral}`), graphite-warm ink (`{colors.primary}`), and vermilion diagram annotations (`{colors.tertiary}`)—built strictly to convey dense technical truth without ornament.",
            "#1E1A14",
            "#FFFFFF",
            "#5C5549",
            "#FFFFFF",
            "#A8321E",
            "#FFFFFF",
            "#F4F0E4",
            "#FAF7EE",
            "#1E1A14",
            "#B8B0A2",
            "#991B1B",
            "#FFFFFF",
            "Source Serif 4",
            "JetBrains Mono",
        ),
    ),
]:
    (
        _desc,
        _ov,
        _pri,
        _on_pri,
        _sec,
        _on_sec,
        _ter,
        _on_ter,
        _neu,
        _surf,
        _on_surf,
        _outl,
        _err,
        _on_err,
        _font_main,
        _font_mono,
    ) = _arch_cfg
    ARCHETYPES[_arch_key] = {
        "description": _desc,
        "overview": _ov,
        "colors": {
            "primary": _pri,
            "on-primary": _on_pri,
            "secondary": _sec,
            "on-secondary": _on_sec,
            "tertiary": _ter,
            "on-tertiary": _on_ter,
            "neutral": _neu,
            "surface": _surf,
            "on-surface": _on_surf,
            "outline": _outl,
            "error": _err,
            "on-error": _on_err,
        },
        "colors_prose": [
            "**Primary (`{colors.primary}`)**: Primary ink for headings and core text paired with `{colors.on-primary}`.",
            "**Secondary (`{colors.secondary}`)**: Supporting tone for metadata, captions, and secondary badges paired with `{colors.on-secondary}`.",
            "**Tertiary (`{colors.tertiary}`)**: Intentional interactive accent for primary CTAs paired with `{colors.on-tertiary}`.",
            "**Neutral (`{colors.neutral}`) & Surface (`{colors.surface}`)**: Base page canvas and elevated card surface with `{colors.on-surface}` text and `{colors.outline}` borders.",
            "**Error (`{colors.error}`)**: Semantic alert state paired with `{colors.on-error}`.",
        ],
        "typography": {
            "h1": {
                "fontFamily": _font_main,
                "fontSize": "44px",
                "fontWeight": 600,
                "lineHeight": 1.15,
                "letterSpacing": "-0.02em",
            },
            "h2": {
                "fontFamily": _font_main,
                "fontSize": "28px",
                "fontWeight": 600,
                "lineHeight": 1.25,
            },
            "body-md": {
                "fontFamily": _font_main,
                "fontSize": "16px",
                "fontWeight": 400,
                "lineHeight": 1.6,
            },
            "label-sm": {
                "fontFamily": _font_mono,
                "fontSize": "12px",
                "fontWeight": 500,
                "lineHeight": 1.2,
                "letterSpacing": "0.05em",
            },
        },
        "typography_prose": (
            f"Combines **{_font_main}** for primary reading hierarchy (`h1`, `h2`, `body-md`) with "
            f"**{_font_mono}** (`label-sm`) for structured identifiers, numerals, and compact labels."
        ),
        "spacing": {
            "xs": "4px",
            "sm": "8px",
            "md": "16px",
            "lg": "24px",
            "xl": "48px",
            "gutter": "24px",
            "margin": "32px",
        },
        "layout_prose": (
            "Uses an `8px` spatial grid (`{spacing.xs}` half-step) with `{spacing.gutter}` column gutters "
            "and `{spacing.margin}` page margins. Content groups are structured inside `{colors.surface}` containers."
        ),
        "elevation_prose": (
            "Visual hierarchy relies on tonal contrast between `{colors.neutral}` and `{colors.surface}` "
            "reinforced by `1px solid` `{colors.outline}` structural borders."
        ),
        "rounded": {
            "none": "0px",
            "sm": "4px",
            "md": "8px",
            "lg": "16px",
            "full": "9999px",
        },
        "shapes_prose": (
            "Uses `{rounded.sm}` for interactive controls, `{rounded.md}` for cards and dialogs, "
            "and `{rounded.full}` for semantic status pills."
        ),
        "components": {
            "button-primary": {
                "backgroundColor": "{colors.tertiary}",
                "textColor": "{colors.on-tertiary}",
                "typography": "{typography.label-sm}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
                "height": "44px",
            },
            "button-secondary": {
                "backgroundColor": "{colors.primary}",
                "textColor": "{colors.on-primary}",
                "typography": "{typography.label-sm}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
                "height": "44px",
            },
            "card-surface": {
                "backgroundColor": "{colors.surface}",
                "textColor": "{colors.on-surface}",
                "rounded": "{rounded.md}",
                "padding": "{spacing.lg}",
            },
            "badge-muted": {
                "backgroundColor": "{colors.secondary}",
                "textColor": "{colors.on-secondary}",
                "typography": "{typography.label-sm}",
                "rounded": "{rounded.full}",
                "padding": "{spacing.xs}",
            },
            "alert-error": {
                "backgroundColor": "{colors.error}",
                "textColor": "{colors.on-error}",
                "typography": "{typography.body-md}",
                "rounded": "{rounded.sm}",
                "padding": "{spacing.md}",
            },
        },
        "components_prose": [
            "**Buttons (`button-primary`, `button-secondary`)**: `44px` minimum height, `{rounded.sm}` radius, and high-contrast `{colors.on-tertiary}` / `{colors.on-primary}` labels.",
            "**Cards (`card-surface`)**: `{colors.surface}` container with `{spacing.lg}` padding and `1px` `{colors.outline}` border.",
            "**Badges & Alerts (`badge-muted`, `alert-error`)**: Semantic status indicators bound to `{colors.secondary}` and `{colors.error}`.",
        ],
        "dos_and_donts": [
            "**Do** keep every component bound to semantic `{colors.*}`, `{typography.*}`, `{rounded.*}`, and `{spacing.*}` tokens.",
            "**Do** enforce WCAG 2.2 AA contrast (`>= 4.5:1`) across all component `backgroundColor` and `textColor` pairs.",
            "**Don't** invent ad-hoc inline hex values or arbitrary pixel spacing outside the token scale.",
            "**Don't** add generic AI-slop decorative blurs, neon orbs, or unrequested marketing carousels.",
        ],
    }


def render_yaml_map(key: str, mapping: dict[str, Any], indent: int = 0) -> list[str]:
    """Serialize a nested token dictionary into clean YAML lines."""
    pad = " " * indent
    lines = [f"{pad}{key}:"]
    for k, v in mapping.items():
        if isinstance(v, dict):
            lines.extend(render_yaml_map(str(k), v, indent + 2))
        elif isinstance(v, (int, float)):
            lines.append(f"{pad}  {k}: {v}")
        else:
            s_val = str(v)
            if s_val.startswith(("#", "{")) or ":" in s_val or " " in s_val:
                lines.append(f'{pad}  {k}: "{s_val}"')
            else:
                lines.append(f"{pad}  {k}: {s_val}")
    return lines


def build_design_md(
    name: str,
    archetype_key: str = "editorial-prestige",
    layout_mode: str = "frontmatter",
    hydrated_colors: dict[str, str] | None = None,
) -> str:
    """Build a complete DESIGN.md document in frontmatter or interleaved mode."""
    spec = ARCHETYPES.get(archetype_key, ARCHETYPES["editorial-prestige"])
    colors = dict(spec["colors"])
    if hydrated_colors:
        for k in ("primary", "secondary", "tertiary", "neutral", "surface", "error"):
            if k in hydrated_colors and hydrated_colors[k].startswith("#"):
                colors[k] = hydrated_colors[k]

    typography = spec["typography"]
    rounded = spec["rounded"]
    spacing = spec["spacing"]
    components = spec["components"]

    lines: list[str] = [
        "---",
        'version: "alpha"',
        f'name: "{name}"',
        f'description: "{spec["description"]}"',
    ]

    if layout_mode == "frontmatter":
        lines.extend(render_yaml_map("colors", colors))
        lines.extend(render_yaml_map("typography", typography))
        lines.extend(render_yaml_map("rounded", rounded))
        lines.extend(render_yaml_map("spacing", spacing))
        lines.extend(render_yaml_map("components", components))
    lines.append("---")
    lines.append("")

    # 1. Overview
    lines.extend(["## Overview", "", spec["overview"], ""])

    # 2. Colors
    lines.extend(["## Colors", ""])
    if layout_mode == "interleaved":
        lines.append("```yaml")
        lines.extend(render_yaml_map("colors", colors))
        lines.extend(["```", ""])
    lines.append(
        "The color palette pairs descriptive character names with normative system tokens:"
    )
    lines.append("")
    for bullet in spec["colors_prose"]:
        lines.append(f"- {bullet}")
    lines.append("")

    # 3. Typography
    lines.extend(["## Typography", ""])
    if layout_mode == "interleaved":
        lines.append("```yaml")
        lines.extend(render_yaml_map("typography", typography))
        lines.extend(["```", ""])
    lines.extend([spec["typography_prose"], ""])

    # 4. Layout
    lines.extend(["## Layout", ""])
    if layout_mode == "interleaved":
        lines.append("```yaml")
        lines.extend(render_yaml_map("spacing", spacing))
        lines.extend(["```", ""])
    lines.extend([spec["layout_prose"], ""])

    # 5. Elevation & Depth
    lines.extend(["## Elevation & Depth", "", spec["elevation_prose"], ""])

    # 6. Shapes
    lines.extend(["## Shapes", ""])
    if layout_mode == "interleaved":
        lines.append("```yaml")
        lines.extend(render_yaml_map("rounded", rounded))
        lines.extend(["```", ""])
    lines.extend([spec["shapes_prose"], ""])

    # 7. Components
    lines.extend(["## Components", ""])
    if layout_mode == "interleaved":
        lines.append("```yaml")
        lines.extend(render_yaml_map("components", components))
        lines.extend(["```", ""])
    for bullet in spec["components_prose"]:
        lines.append(f"- {bullet}")
    lines.append("")

    # 8. Do's and Don'ts
    lines.extend(["## Do's and Don'ts", ""])
    for rule in spec["dos_and_donts"]:
        lines.append(f"- {rule}")
    lines.append("")

    return "\n".join(lines)


def convert_prose_stitch_to_hybrid(prose_path: Path, name: str, layout_mode: str) -> str:
    """Convert a pure-prose Stitch DESIGN.md export into a hybrid YAML+prose DESIGN.md."""
    raw = prose_path.read_text(encoding="utf-8", errors="replace")
    hex_matches = re.findall(r"#[0-9A-Fa-f]{6}\b", raw)
    hydrated: dict[str, str] = {}
    roles = ["primary", "secondary", "tertiary", "neutral", "surface"]
    for idx, hex_val in enumerate(hex_matches[: len(roles)]):
        hydrated[roles[idx]] = hex_val
    return build_design_md(
        name=name,
        archetype_key="editorial-prestige",
        layout_mode=layout_mode,
        hydrated_colors=hydrated,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a spec-compliant DESIGN.md file for AI coding and design agents."
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Target project directory (default: current directory).",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="",
        help="Design system or brand name (defaults to project directory name).",
    )
    parser.add_argument(
        "--archetype",
        choices=list(ARCHETYPES.keys()),
        default="",
        help="Design system archetype template.",
    )
    parser.add_argument(
        "--layout",
        choices=["frontmatter", "interleaved"],
        default="frontmatter",
        help="Token embedding layout: YAML frontmatter (default) or interleaved YAML blocks.",
    )
    parser.add_argument(
        "--hydrate",
        action="store_true",
        help="Hydrate palette with existing hex colors discovered in the project.",
    )
    parser.add_argument(
        "--from-prose",
        type=Path,
        default=None,
        help="Convert a pure-prose Stitch DESIGN.md file into a hybrid spec-compliant DESIGN.md.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="DESIGN.md",
        help="Output file path (default: DESIGN.md, or '-' for stdout).",
    )
    args = parser.parse_args()

    inspection = inspect_project_design(args.project_dir)
    brand_name = args.name or str(inspection["project_name"]).replace("-", " ").title()
    archetype = args.archetype or str(inspection["recommended_archetype"])

    if args.from_prose:
        content = convert_prose_stitch_to_hybrid(args.from_prose, brand_name, args.layout)
    else:
        hydrated = inspection["discovered_tokens"]["colors"] if args.hydrate else None
        content = build_design_md(
            name=brand_name,
            archetype_key=archetype,
            layout_mode=args.layout,
            hydrated_colors=hydrated,
        )

    if args.output == "-":
        print(content)
    else:
        out_path = Path(args.output)
        out_path.write_text(content, encoding="utf-8")
        print(f"Generated DESIGN.md ({args.layout} mode, archetype='{archetype}') -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

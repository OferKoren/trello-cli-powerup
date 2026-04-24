# Power-Up Icons Design

**Date:** 2026-04-24
**Scope:** Replace placeholder SVG circles in `powerup/icons/` with meaningful icons; add Policies board-button icon.

## Goal

The AC Workflow Power-Up currently ships three placeholder monochrome circles as icons. This spec defines the final SVG designs for:

1. **Power-Up icon** — 3 variants (light, dark, gray) used by Trello in the Power-Up directory and board header.
2. **Policies board-button icon** — single gray variant used as the icon beside the "Agent Policies" board-button label.

## Design Decisions

**Style:** Minimal/geometric, stroke-only (no fills on shapes), rounded linecaps. Matches Atlassian/Trello's own icon language.

**Power-Up metaphor:** Two interlocked circles — represents the agent collaboration loop (human ↔ Claude).

**Policies metaphor:** Checklist document — a document outline with three bulleted rule lines. Matches the "policy items" mental model.

## Icon Specifications

### Power-Up icon — interlocked circles

`viewBox="0 0 48 48"`, scalable SVG. Three color variants:

| File | Stroke color | Intended background |
|---|---|---|
| `icons/icon-light.svg` | `#0052cc` (Trello blue) | Light / white backgrounds |
| `icons/icon-dark.svg` | `#ffffff` | Dark backgrounds |
| `icons/icon-gray.svg` | `#97a0af` | Inactive / default state |

Shape: two circles, `r=11`, centers at `(17,24)` and `(31,24)`, `stroke-width=3.5`. No fill.

### Policies board-button icon — checklist

`viewBox="0 0 24 24"`, scalable SVG. Single file: `icons/icon-policies.svg`.

Shape: rounded-rect outline (`rx=2`, `16×18` at `(4,3)`), three rows each with a filled circle bullet (`r=1.2`) at x=7.5 and a horizontal line from x=10 to x=16 (last row to x=14). Stroke/fill color: `#97a0af`. No other colors.

Referenced in `powerup/client.js` `board-buttons` capability as the button icon.

## Files Changed

| File | Action |
|---|---|
| `powerup/icons/icon-light.svg` | Replace placeholder circle |
| `powerup/icons/icon-dark.svg` | Replace placeholder circle |
| `powerup/icons/icon-gray.svg` | Replace placeholder circle |
| `powerup/icons/icon-policies.svg` | New file |
| `powerup/client.js` | Add `POLICIES_ICON` constant; wire into board-buttons |

## Out of Scope

- Animated icons
- PNG/raster exports
- Icon for card-back-section (uses `icon-gray.svg` already)
- Any icon size other than the existing SVG viewBox dimensions

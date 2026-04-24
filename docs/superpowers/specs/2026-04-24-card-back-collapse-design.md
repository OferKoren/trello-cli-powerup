# Card-Back Agent Panel Collapse — Design Spec

## Goal

Make the "Agent" card-back-section iframe collapsed by default. Users expand it on demand. State persists per card via Trello storage.

## Context

The Power-Up renders a `card-back-section` (Trello's name for a power-up section on the card back) pointing to `plan.html` at 600px height. This is always expanded when a card opens, cluttering the card back alongside Trello's native Custom Fields section. The user wants it collapsed by default, expandable on click.

The Trello-rendered "Agent" section header (icon + title) remains — we only control the iframe content and its height.

## Files Changed

| File | Change |
|------|--------|
| `powerup/client.js` | `height: 600` → `height: 36` |
| `powerup/plan.html` | Add `#collapse-toggle` row; wrap existing content in `#panel-body` (hidden by default) |
| `powerup/plan.js` | Add toggle logic, `t.sizeTo()` calls, Trello card storage read/write |

No new files.

## Collapsed State (default)

Iframe height: 36px. Content:

```
▶  Agent Panel          (full-width row, cursor pointer, muted style)
```

Trello's own "Agent" section header (with gray icon) is rendered above by Trello — not in our iframe.

## Expanded State

Iframe resizes to fit full content via `t.sizeTo(document.body)`. Content:

```
▼  Agent Panel
[tabs: Plan | Manual Testing v2]
... existing plan.html content ...
```

## State Management

- **Storage:** `t.get('card', 'shared', 'agentPanelExpanded')` — boolean, per-card, shared across users
- **Default:** `false` (collapsed)
- **On load:** read state → render accordingly → call `t.sizeTo()` to set iframe height
- **On toggle click:** flip value → `t.set(...)` → update DOM → `t.sizeTo()`
- **Collapsed sizeTo target:** `#collapse-toggle` element (36px)
- **Expanded sizeTo target:** `document.body` (auto-fit full content)

## Behaviour Rules

- Always starts collapsed on first open (no stored state)
- After user expands: stays expanded for that card on future opens
- After user collapses: stays collapsed
- `t.sizeTo()` called after every toggle to keep iframe height in sync with content

## Non-Goals

- No animation
- No change to Custom Fields section (Trello-native, uncontrollable)
- No change to card-badges or card-detail-badges (keep working status indicator)

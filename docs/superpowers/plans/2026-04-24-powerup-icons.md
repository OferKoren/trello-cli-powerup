# Power-Up Icons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 3 placeholder circle SVGs and add a Policies board-button icon so the AC Workflow Power-Up has meaningful, on-brand icons in Trello.

**Architecture:** Pure SVG file replacements (no build step) plus one `var` addition and one property change in `client.js`. No tests — SVGs are static assets verified visually after deploy.

**Tech Stack:** SVG 1.1, plain ES5 JavaScript (`powerup/client.js`)

---

### Task 1: Replace Power-Up icon SVGs (light, dark, gray)

**Files:**
- Modify: `powerup/icons/icon-light.svg`
- Modify: `powerup/icons/icon-dark.svg`
- Modify: `powerup/icons/icon-gray.svg`

Spec: two interlocked circles, `viewBox="0 0 48 48"`, centers at `(17,24)` and `(31,24)`, `r=11`, `stroke-width=3.5`, no fill.

- [ ] **Step 1: Write icon-light.svg** (blue stroke for light backgrounds)

Replace entire file with:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <circle cx="17" cy="24" r="11" fill="none" stroke="#0052cc" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="31" cy="24" r="11" fill="none" stroke="#0052cc" stroke-width="3.5" stroke-linecap="round"/>
</svg>
```

- [ ] **Step 2: Write icon-dark.svg** (white stroke for dark backgrounds)

Replace entire file with:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <circle cx="17" cy="24" r="11" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="31" cy="24" r="11" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>
</svg>
```

- [ ] **Step 3: Write icon-gray.svg** (gray stroke for inactive/default state)

Replace entire file with:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <circle cx="17" cy="24" r="11" fill="none" stroke="#97a0af" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="31" cy="24" r="11" fill="none" stroke="#97a0af" stroke-width="3.5" stroke-linecap="round"/>
</svg>
```

- [ ] **Step 4: Commit**

```bash
git add powerup/icons/icon-light.svg powerup/icons/icon-dark.svg powerup/icons/icon-gray.svg
git commit -m "feat: replace placeholder circles with interlocked-circle Power-Up icons"
```

---

### Task 2: Create Policies board-button icon

**Files:**
- Create: `powerup/icons/icon-policies.svg`

Spec: `viewBox="0 0 24 24"`, rounded-rect outline (`rx=2`, `16×18` at `(4,3)`), three rows each with a filled circle bullet (`r=1.2`, x=7.5, y=8/12/16) and a horizontal line (x=10→16, last row x=10→14). Stroke/fill: `#97a0af`.

- [ ] **Step 1: Write icon-policies.svg**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <rect x="4" y="3" width="16" height="18" rx="2" fill="none" stroke="#97a0af" stroke-width="1.8"/>
  <circle cx="7.5" cy="8"  r="1.2" fill="#97a0af"/>
  <line x1="10" y1="8"  x2="16" y2="8"  stroke="#97a0af" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="7.5" cy="12" r="1.2" fill="#97a0af"/>
  <line x1="10" y1="12" x2="16" y2="12" stroke="#97a0af" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="7.5" cy="16" r="1.2" fill="#97a0af"/>
  <line x1="10" y1="16" x2="14" y2="16" stroke="#97a0af" stroke-width="1.5" stroke-linecap="round"/>
</svg>
```

- [ ] **Step 2: Commit**

```bash
git add powerup/icons/icon-policies.svg
git commit -m "feat: add policies checklist board-button icon"
```

---

### Task 3: Wire Policies icon into client.js

**Files:**
- Modify: `powerup/client.js` — add `POLICIES_ICON` var at line 5 (after existing icon vars); update `board-buttons` icon property at line ~93.

Current `board-buttons` block (lines 91–106):
```js
'board-buttons': function(t, opts) {
  return [{
    icon: {
      dark:  LIGHT_ICON,
      light: DARK_ICON
    },
    text: 'Agent Policies',
    ...
```

- [ ] **Step 1: Add POLICIES_ICON constant**

In `powerup/client.js`, after line 5 (`var LIGHT_ICON = ...`), add:

```js
var POLICIES_ICON = './icons/icon-policies.svg';
```

- [ ] **Step 2: Update board-buttons icon to use POLICIES_ICON**

Replace the `icon` property in the `board-buttons` return value:

```js
// before:
icon: {
  dark:  LIGHT_ICON,
  light: DARK_ICON
},

// after:
icon: POLICIES_ICON,
```

- [ ] **Step 3: Verify file looks correct**

Top of `powerup/client.js` should now read:
```js
var GRAY_ICON     = './icons/icon-gray.svg';
var DARK_ICON     = './icons/icon-dark.svg';
var LIGHT_ICON    = './icons/icon-light.svg';
var POLICIES_ICON = './icons/icon-policies.svg';
```

And the `board-buttons` block:
```js
'board-buttons': function(t, opts) {
  return [{
    icon: POLICIES_ICON,
    text: 'Agent Policies',
    callback: function(t) { ... }
  }];
},
```

- [ ] **Step 4: Commit**

```bash
git add powerup/client.js
git commit -m "feat: wire policies icon into board-buttons capability"
```

---

### Task 4: Deploy and verify

**Files:** None changed — deploy only.

- [ ] **Step 1: Deploy to Vercel**

```bash
cd powerup && vercel --prod
```

Expected: deployment URL printed (e.g. `https://powerup-peach.vercel.app`).

- [ ] **Step 2: Verify Power-Up icons in Trello**

1. Open the Powerup-dev board in Trello.
2. Open Power-Ups list — confirm AC Workflow shows interlocked circles (not a plain circle).
3. Confirm board header shows the checklist icon beside "Agent Policies".
4. Open a card — confirm card-back section header shows the gray interlocked circles.

- [ ] **Step 3: Commit deploy confirmation** (no code change — just move the Trello card)

```bash
trello card move "first-card" --to "agentic-planned"
trello card state set "first-card" --status planned
```

(Note: `card state set` requires Custom Fields / paid Trello plan — skip if on free plan.)

# Card-Back Agent Panel Collapse — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the "Agent" card-back-section iframe collapsed by default, expandable on click, with state persisted per card via Trello storage.

**Architecture:** The iframe starts at 36px height showing only a toggle row. Clicking the row reads/writes `agentPanelExpanded` from Trello card storage, toggles DOM visibility of `#panel-body`, and calls `t.sizeTo()` to resize the iframe. No new files — three existing files modified.

**Tech Stack:** Vanilla JS (ES5), Trello Power-Up JS SDK (`TrelloPowerUp.iframe()`), HTML/CSS.

---

## File Map

| File | Change |
|------|--------|
| `powerup/client.js` | Line 56: `height: 600` → `height: 36` |
| `powerup/styles.css` | Add `.collapse-toggle` rule |
| `powerup/plan.html` | Add `#collapse-toggle` div; wrap content in `#panel-body` |
| `powerup/plan.js` | Add `togglePanel()`; update `loadPlan()` to restore panel state |

---

### Task 1: Set initial iframe height in client.js

**Files:**
- Modify: `powerup/client.js:49-58`

- [ ] **Step 1: Edit client.js**

Change line 56 from:
```js
        height: 600
```
to:
```js
        height: 36
```

Full updated `card-back-section` block:
```js
  'card-back-section': function(t, opts) {
    return {
      title: 'Agent',
      icon: GRAY_ICON,
      content: {
        type: 'iframe',
        url: t.signUrl('./plan.html'),
        height: 36
      }
    };
  },
```

- [ ] **Step 2: Verify**

Open a Trello card. The "Agent" section on the card back should now be a very thin strip (36px) — the tabs and plan content should not be visible.

- [ ] **Step 3: Commit**

```bash
git add powerup/client.js
git commit -m "feat: set card-back iframe height to 36 (collapsed default)"
```

---

### Task 2: Add collapse toggle styles to styles.css

**Files:**
- Modify: `powerup/styles.css` (append at end)

- [ ] **Step 1: Append to styles.css**

Add at the very end of `powerup/styles.css`:

```css
/* ---- Collapse toggle ---- */
.collapse-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 0;
  font-size: 13px;
  color: #5e6c84;
  user-select: none;
  height: 36px;
}

.collapse-toggle:hover { color: #172b4d; }

.collapse-arrow {
  font-size: 10px;
  transition: transform 0.15s;
}
```

- [ ] **Step 2: Verify**

No visible change yet — style is not applied until HTML uses it (Task 3).

- [ ] **Step 3: Commit**

```bash
git add powerup/styles.css
git commit -m "feat: add collapse-toggle styles"
```

---

### Task 3: Restructure plan.html DOM

**Files:**
- Modify: `powerup/plan.html`

- [ ] **Step 1: Replace plan.html body content**

Replace the entire `<body>` content (lines 9–46) with:

```html
<body>
  <div class="collapse-toggle" id="collapse-toggle" onclick="togglePanel()">
    <span class="collapse-arrow" id="collapse-arrow">&#9654;</span>
    Agent Panel
  </div>

  <div id="panel-body" style="display:none">
    <div class="tabs" role="tablist">
      <button class="tab active" id="tab-plan" role="tab" onclick="switchTab('plan')">Plan</button>
      <button class="tab" id="tab-mt" role="tab" disabled>
        Manual Testing <span class="tab-badge">v2</span>
      </button>
    </div>

    <div id="content-plan" class="tab-content active">
      <div id="agent-status-bar" style="display:none; margin-bottom:12px; font-size:13px;">
        <span class="agent-dot" id="agent-dot"></span>
        <span id="agent-status-text">idle</span>
      </div>

      <label style="font-weight:600; font-size:13px; display:block; margin-bottom:4px;">Plan</label>
      <textarea id="plan-body" class="plan-body" maxlength="3500"
                placeholder="Describe the goal and approach for this feature..."></textarea>

      <label style="font-weight:600; font-size:13px; display:block; margin-bottom:8px; margin-top:4px;">
        Subtasks
      </label>
      <ul id="subtasks" class="subtasks"></ul>
      <button class="btn btn-secondary" onclick="addSubtask()" style="margin-bottom:4px;">+ Add subtask</button>

      <div class="actions">
        <button class="btn btn-primary" onclick="savePlan()">Save</button>
        <button class="btn btn-secondary" onclick="loadPlan()">Reload</button>
      </div>
    </div>

    <div id="content-mt" class="tab-content">
      <p style="color:#5e6c84; font-size:13px; padding:16px; text-align:center;">
        Manual Testing UI coming in v2.
      </p>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <script src="https://p.trellocdn.com/power-up.min.js"></script>
  <script src="./plan.js"></script>
</body>
```

- [ ] **Step 2: Verify structure**

Open the card. The 36px "Agent" section should now show `▶ Agent Panel`. Clicking it will not work yet (JS not wired). The full content (tabs, textarea) should be hidden.

- [ ] **Step 3: Commit**

```bash
git add powerup/plan.html
git commit -m "feat: add collapse toggle row and wrap content in panel-body"
```

---

### Task 4: Wire toggle logic in plan.js

**Files:**
- Modify: `powerup/plan.js`

- [ ] **Step 1: Add togglePanel() function**

Insert after the `switchTab` function (after line 37), before the subtask rendering section:

```js
/* ---- collapse / expand panel ---- */

function applyPanelState(expanded) {
  var body = document.getElementById('panel-body');
  var arrow = document.getElementById('collapse-arrow');
  if (expanded) {
    body.style.display = 'block';
    arrow.innerHTML = '&#9660;'; /* ▼ */
    t.sizeTo(document.body);
  } else {
    body.style.display = 'none';
    arrow.innerHTML = '&#9654;'; /* ▶ */
    t.sizeTo('#collapse-toggle');
  }
}

function togglePanel() {
  t.get('card', 'shared', 'agentPanelExpanded').then(function(current) {
    var next = !current;
    return t.set('card', 'shared', 'agentPanelExpanded', next).then(function() {
      applyPanelState(next);
    });
  });
}
```

- [ ] **Step 2: Update loadPlan() to restore panel state**

Replace the existing `loadPlan` function (lines 149–158):

```js
function loadPlan() {
  return Promise.all([
    t.get('card', 'shared', 'plan'),
    t.get('card', 'shared', 'agentPanelExpanded')
  ]).then(function(results) {
    var plan = results[0];
    var expanded = results[1] === true;
    if (plan && typeof plan === 'object') {
      populateForm(plan);
    }
    return updateAgentDot().then(function() {
      applyPanelState(expanded);
    });
  });
}
```

- [ ] **Step 3: Verify toggle behavior**

1. Open a Trello card. "Agent" section shows `▶ Agent Panel` (36px, collapsed).
2. Click the toggle row → panel expands, arrow becomes `▼`, full content visible.
3. Click again → collapses back to `▶`, 36px.
4. Close and reopen the card → panel remembers its last state (expanded or collapsed).
5. On a fresh card (no stored state) → panel starts collapsed.

- [ ] **Step 4: Commit**

```bash
git add powerup/plan.js
git commit -m "feat: wire collapse toggle with Trello card storage and t.sizeTo"
```

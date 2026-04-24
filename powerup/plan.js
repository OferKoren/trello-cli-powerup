/* global TrelloPowerUp */

var t = TrelloPowerUp.iframe();

var MODEL_OPTIONS = ['haiku', 'sonnet', 'opus', 'dynamic'];
var AGENT_OPTIONS = [
  'brainstorming', 'writing-plans', 'subagent-driven-development',
  'test-driven-development', 'systematic-debugging',
  'receiving-code-review', 'finishing-a-development-branch'
];

/* ---- utilities ---- */

function arrayFind(arr, fn) {
  for (var i = 0; i < arr.length; i++) {
    if (fn(arr[i])) return arr[i];
  }
  return undefined;
}

function uid() {
  return 'st' + Math.random().toString(36).slice(2, 9);
}

function showToast(msg) {
  var el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(function() { el.classList.remove('show'); }, 2000);
}

function switchTab(name) {
  Array.prototype.forEach.call(document.querySelectorAll('.tab'), function(b) { b.classList.remove('active'); });
  Array.prototype.forEach.call(document.querySelectorAll('.tab-content'), function(d) { d.classList.remove('active'); });
  document.getElementById('tab-' + name).classList.add('active');
  document.getElementById('content-' + name).classList.add('active');
}

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

/* ---- subtask rendering ---- */

function buildSelect(options, selectedValue, cls) {
  var sel = document.createElement('select');
  sel.className = cls;
  options.forEach(function(opt) {
    var o = document.createElement('option');
    o.value = opt;
    o.textContent = opt;
    if (opt === selectedValue) o.selected = true;
    sel.appendChild(o);
  });
  return sel;
}

function renderSubtask(st) {
  var li = document.createElement('li');
  li.className = 'subtask-row';
  li.setAttribute('data-id', st.id);

  var cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = !!st.done;

  var txt = document.createElement('input');
  txt.type = 'text';
  txt.className = 'subtask-text';
  txt.value = st.text || '';
  txt.placeholder = 'Task description…';

  var modelSel = buildSelect(MODEL_OPTIONS, st.model || 'sonnet', 'subtask-select');
  var agentSel = buildSelect(AGENT_OPTIONS, st.agent || AGENT_OPTIONS[0], 'subtask-select');

  var rm = document.createElement('button');
  rm.className = 'remove-btn';
  rm.textContent = '\xd7';
  rm.onclick = function() { li.remove(); };

  li.appendChild(cb);
  li.appendChild(txt);
  li.appendChild(modelSel);
  li.appendChild(agentSel);
  li.appendChild(rm);
  return li;
}

function addSubtask(st) {
  var data = st || { id: uid(), text: '', done: false, model: 'sonnet', agent: AGENT_OPTIONS[0] };
  document.getElementById('subtasks').appendChild(renderSubtask(data));
}

/* ---- read form state ---- */

function readForm() {
  var subtasks = [];
  Array.prototype.forEach.call(document.querySelectorAll('#subtasks .subtask-row'), function(li) {
    var inputs = li.querySelectorAll('input');
    var selects = li.querySelectorAll('select');
    subtasks.push({
      id: li.getAttribute('data-id') || uid(),
      done: inputs[0].checked,
      text: inputs[1].value,
      model: selects[0].value,
      agent: selects[1].value,
      rejection_reason: null
    });
  });
  return {
    schema: 1,
    body: document.getElementById('plan-body').value,
    body_ref: null,
    subtasks: subtasks
  };
}

/* ---- populate form from data ---- */

function populateForm(plan) {
  document.getElementById('plan-body').value = plan.body || '';
  var ul = document.getElementById('subtasks');
  ul.innerHTML = '';
  (plan.subtasks || []).forEach(function(st) { addSubtask(st); });
}

/* ---- agent status dot ---- */

function updateAgentDot() {
  return Promise.all([
    t.card('customFieldItems'),
    t.board('customFields')
  ]).then(function(results) {
    var items = results[0].customFieldItems || [];
    var fields = results[1].customFields || [];
    var statusField = arrayFind(fields, function(f) { return f.name === 'agent_status'; });
    if (!statusField) return;
    var item = arrayFind(items, function(i) { return i.idCustomField === statusField.id; });
    if (!item) return;
    var opt = arrayFind(statusField.options || [], function(o) { return o.id === item.idValue; });
    var status = opt ? opt.value.text : 'idle';
    var bar = document.getElementById('agent-status-bar');
    var dot = document.getElementById('agent-dot');
    var txt = document.getElementById('agent-status-text');
    bar.style.display = 'block';
    txt.textContent = status;
    dot.className = 'agent-dot ' + status;
  }).catch(function() {});
}

/* ---- load / save ---- */

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

function savePlan() {
  var data = readForm();
  t.set('card', 'shared', 'plan', data).then(function() {
    showToast('Plan saved.');
  }).catch(function(err) {
    showToast('Error saving: ' + (err && err.message ? err.message : String(err)));
  });
}

/* ---- init ---- */

t.render(function() {
  return loadPlan();
});

/* global TrelloPowerUp, POWERUP_VERSION */

var t = TrelloPowerUp.iframe();

var BUILT_IN_POLICIES = [
  {
    id: 'use-superpowers',
    title: 'Use superpowers skills',
    body: 'All agent work must go through the superpowers plugin. The required sequence is: brainstorming → writing-plans → subagent-driven-development (or executing-plans). Do not start implementation without a written plan.'
  },
  {
    id: 'spec-and-plan',
    title: 'Create spec.md and plan.md on feature start',
    body: 'Before moving a card to agentic-implementing, the session must produce a spec.md (from brainstorming) and a plan.md (from writing-plans) and attach both to the card. The spec_attached and plan_attached Custom Fields must be true.'
  },
  {
    id: 'feature-map',
    title: 'Create feature-file map in spec',
    body: 'Every spec.md must include a "Feature Map" section: a table mapping feature domains (e.g. Auth, Payments) to the files they touch. This map is used by subagents for scoped context during implementation.'
  }
];

function renderPolicies() {
  var ul = document.getElementById('policies');
  BUILT_IN_POLICIES.forEach(function(p) {
    var li = document.createElement('li');
    li.className = 'policy-item';

    var header = document.createElement('div');
    header.className = 'policy-header';
    header.innerHTML =
      '<span>' + p.title + '</span>' +
      '<span class="policy-badge">built-in</span>';
    header.onclick = function() {
      var body = li.querySelector('.policy-body');
      body.classList.toggle('open');
    };

    var body = document.createElement('div');
    body.className = 'policy-body';
    body.textContent = p.body;

    li.appendChild(header);
    li.appendChild(body);
    ul.appendChild(li);
  });
}

t.render(function() {
  renderPolicies();
  t.sizeTo('#policies');
});

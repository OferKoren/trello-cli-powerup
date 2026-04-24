/* global TrelloPowerUp */

var GRAY_ICON  = './icons/icon-gray.svg';
var DARK_ICON  = './icons/icon-dark.svg';
var LIGHT_ICON = './icons/icon-light.svg';

/* ---- helpers ---- */

var AGENT_FIELDS = ['agent_status', 'branch', 'worktree_path', 'model_tag',
                    'agent_tag', 'last_run_at', 'spec_attached', 'plan_attached'];

function getAgentStatus(t) {
  return Promise.all([
    t.card('customFieldItems'),
    t.board('customFields')
  ]).then(function(results) {
    var items = results[0].customFieldItems || [];
    var fields = results[1].customFields || [];
    var statusField = fields.find(function(f) { return f.name === 'agent_status'; });
    if (!statusField) return 'idle';
    var item = items.find(function(i) { return i.idCustomField === statusField.id; });
    if (!item || !item.idValue) return 'idle';
    var opt = (statusField.options || []).find(function(o) { return o.id === item.idValue; });
    return opt ? opt.value.text : 'idle';
  }).catch(function() { return 'idle'; });
}

function statusColor(status, tick) {
  if (status === 'working') {
    // Alternate green/lime every 10s for simulated pulse
    return tick % 2 === 0 ? 'green' : 'lime';
  }
  if (status === 'rejected') return 'red';
  if (status === 'approved') return 'purple';
  if (status === 'merged')   return 'blue';
  return 'light-gray';
}

/* ---- initialize ---- */

TrelloPowerUp.initialize({

  'card-back-section': function(t, opts) {
    return {
      title: 'Agent',
      icon: GRAY_ICON,
      content: {
        type: 'iframe',
        url: t.signUrl('./plan.html'),
        height: 600
      }
    };
  },

  'card-detail-badges': function(t, opts) {
    return [{
      dynamic: function() {
        return getAgentStatus(t).then(function(status) {
          return {
            title: 'Agent',
            text: status,
            color: statusColor(status, 0),
            refresh: 10
          };
        });
      }
    }];
  },

  'card-badges': function(t, opts) {
    return [{
      dynamic: function() {
        var tick = Math.floor(Date.now() / 10000);
        return getAgentStatus(t).then(function(status) {
          return {
            text: status === 'working' ? 'working' : null,
            color: statusColor(status, tick),
            refresh: 10
          };
        });
      }
    }];
  },

  'board-buttons': function(t, opts) {
    return [{
      icon: {
        dark:  LIGHT_ICON,
        light: DARK_ICON
      },
      text: 'Agent Policies',
      callback: function(t) {
        return t.modal({
          title: 'Agent Policies',
          url: t.signUrl('./policies.html'),
          height: 500
        });
      }
    }];
  },

  'show-settings': function(t, opts) {
    return t.popup({
      title: 'Agent Settings',
      url: t.signUrl('./settings.html'),
      height: 300
    });
  }

});

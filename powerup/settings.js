/* global TrelloPowerUp, POWERUP_VERSION */

var t = TrelloPowerUp.iframe();

function saveSettings() {
  var url = document.getElementById('cli-base-url').value.trim();
  t.set('board', 'private', 'cliBaseUrl', url).then(function() {
    document.getElementById('version-display').textContent =
      'Saved. Agent Power-Up v' + POWERUP_VERSION;
  }).catch(function() {
    document.getElementById('version-display').textContent = 'Error saving settings.';
  });
}

t.render(function() {
  document.getElementById('version-display').textContent =
    'Agent Power-Up v' + POWERUP_VERSION;
  return t.get('board', 'private', 'cliBaseUrl').then(function(url) {
    if (url) {
      document.getElementById('cli-base-url').value = url;
    }
    t.sizeTo('body');
  });
});

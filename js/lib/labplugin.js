var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'dagWidget:plugin',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'dagWidget',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};


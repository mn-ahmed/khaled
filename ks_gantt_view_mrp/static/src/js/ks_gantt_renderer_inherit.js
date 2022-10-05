odoo.define("ks_gantt_view_mrp.KsGantt", function (require) {
  "use strict";

  var KsGanttRenderer = require("ks_gantt_view.Renderer");
  var core = require("web.core");

  var ksGanttRendererMRP = KsGanttRenderer.include({
    willStart: function () {
      var ks_def;
      var ks_super = this._super();
      if (this.ks_model_name == "mrp.production") {
        ks_def = this._rpc({
          model: "mrp.gantt.settings",
          method: "ks_get_gantt_view_mrp_settings",
          args: [],
        }).then(
          function (result) {
            this.ks_enable_task_dynamic_text =
              result.ks_enable_task_dynamic_text;
            this.ks_enable_task_dynamic_progress = false;
            this.ks_enable_quickinfo_extension =
              result.ks_enable_quickinfo_extension;
            this.ks_project_tooltip_config = result.ks_project_tooltip_config
              ? result.ks_project_tooltip_config
              : false;
          }.bind(this)
        );
      } else if (this.ks_model_name == "mrp.workorder") {
        ks_def = this._rpc({
          model: "mrp.gantt.settings",
          method: "ks_get_gantt_view_mrp_settings_wo",
          args: [],
        }).then(
          function (result) {
            this.ks_enable_task_dynamic_text =
              result.ks_enable_task_dynamic_text;
            this.ks_enable_task_dynamic_progress =
              result.ks_enable_task_dynamic_progress;
            this.ks_enable_quickinfo_extension =
              result.ks_enable_quickinfo_extension;
            this.ks_project_tooltip_config = result.ks_project_tooltip_config
              ? result.ks_project_tooltip_config
              : false;
          }.bind(this)
        );
      }
      return Promise.all([ks_def, ks_super]);
    },
  });

  return ksGanttRendererMRP;
});

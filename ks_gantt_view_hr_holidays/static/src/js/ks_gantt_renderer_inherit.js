odoo.define("ks_gantt_view_hr_holidays.KsGantt", function (require) {
  "use strict";

  var KsGanttRenderer = require("ks_gantt_view.Renderer");
  var core = require("web.core");

  var ksGanttRendererHrHolidays = KsGanttRenderer.include({
    ks_compute_task_drag: function (each_task) {
      if (this.ks_model_name == "hr.leave" && each_task.state == "validate") {
        return true;
      }
      return this._super(each_task);
    },

    ks_task_drag_and_drop: function () {
      if (this.ks_model_name == "hr.leave") {
        gantt.config.order_branch = false;
        gantt.config.order_branch_free = false;
      } else {
        this._super();
      }
    },

    willStart: function () {
      var ks_def;
      var ks_super = this._super();
      if (this.ks_model_name == "hr.leave") {
        ks_def = this._rpc({
          model: "hr.leave.gantt.settings",
          method: "ks_get_gantt_view_settings",
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
      }
      return Promise.all([ks_def, ks_super]);
    },
  });

  return ksGanttRendererHrHolidays;
});

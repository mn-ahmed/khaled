odoo.define("ks_gantt_view_project.Controller", function (require) {
  "use strict";

  var ksGanttController = require("ks_gantt_view.Controller");
  var framework = require("web.framework");

  ksGanttController.include({
    _ksExportReport: function (ev) {
      var ks_report_type = $(ev.currentTarget).attr("report_type");
      if (
        ks_report_type == "excel" &&
        (this.modelName == "project.task" ||
          this.modelName == "project.project")
      ) {
        framework.blockUI();
        this.getSession().get_file({
          url: "/web/ksgantt/export/xlsx/",
          data: {
            project_id: this.model.context.default_project_id
              ? this.model.context.default_project_id
              : false,
          },
          complete: framework.unblockUI,
          error: (error) => this.call("crash_manager", "rpc_error", error),
        });
      } else this._super(ev);
    },
  });
});

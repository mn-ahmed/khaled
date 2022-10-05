odoo.define("ks_gantt_view.View", function (require) {
  "use strict";

  var AbstractView = require("web.AbstractView");
  var view_registry = require("web.view_registry");
  var core = require("web.core");
  var ksGanttController = require("ks_gantt_view.Controller");
  var ksGanttModel = require("ks_gantt_view.Model");
  var ksGanttRenderer = require("ks_gantt_view.Renderer");
  var pyUtils = require("web.py_utils");
  var _t = core._t;
  var _lt = core._lt;

  var KsGanttView = AbstractView.extend({
    display_name: _lt("Gantt View"),
    icon: "fa-tasks",
    config: _.extend({}, AbstractView.prototype.config, {
      Model: ksGanttModel,
      Controller: ksGanttController,
      Renderer: ksGanttRenderer,
    }),
    viewType: "ks_gantt",
    type: "Gantt",
    multi_record: true,
    searchable: true,
    withControlPanel: true,

    init: function (viewInfo, params) {
      this._super.apply(this, arguments);
      var arch = this.arch;
      var ks_requiredFields = [];
      _.each(arch.children, function (child) {
        if (child.tag === "field") {
          ks_requiredFields.push(child.attrs.name);
        }
      });

      var ks_formViewId = arch.attrs.form_view_id
        ? parseInt(arch.attrs.form_view_id, 10)
        : false;
      if (params.action && !ks_formViewId) {
        var result = _.findWhere(params.action.views, {
          type: "form",
        });
        ks_formViewId = result ? result.viewID : false;
      }
      var ks_dialogViews = [[ks_formViewId, "form"]];

      // Check gantt view attributes.
      var ks_no_drag =
        arch.attrs && arch.attrs.ks_no_drag == "true" ? true : false;
      var ks_hide_links =
        arch.attrs && arch.attrs.ks_hide_links == "true" ? true : false;
      // If links is visible but task link data is not available then hide the link.
      if (!ks_hide_links && !arch.attrs.ks_task_link) {
        ks_hide_links = true;
      }

      this.controllerParams.context = params.context || {};
      this.controllerParams.ks_dialogViews = ks_dialogViews;
      this.loadParams.ks_requiredFields = ks_requiredFields;
      this.loadParams.ks_defaultGroupBy = this.arch.attrs.default_group_by;
      this.loadParams.name = this.arch.attrs.name;
      this.loadParams.date_deadline = this.arch.attrs.date_deadline;
      this.loadParams.fields = this.fields;
      this.rendererParams.ks_isCreate =
        this.controllerParams.activeActions.create;
      this.rendererParams.ks_isEdit = this.controllerParams.activeActions.edit;
      this.rendererParams.ks_no_drag = ks_no_drag;
      this.rendererParams.ks_hide_links = ks_hide_links;
      this.rendererParams.active_id = params.context.active_id;
      this.rendererParams.ks_fieldDetail = viewInfo.fields;
      this.rendererParams.string = arch.attrs.string || _t("Gantt View");
      this.rendererParams.ks_model_name = this.modelParams.modelName;
      this.ks_manage_gantt_arch();
      // Add arch fields to model and renderer.
      this.loadParams.ks_gantt_arch = arch.attrs;
      this.rendererParams.ks_gantt_arch = arch.attrs;
    },

    /**
     * Function to parse Json data in ks gantt arch.
     */
    ks_manage_gantt_arch: function () {
      var ks_gantt_no_field = this.ks_get_gantt_no_field_attribute();

      ks_gantt_no_field.forEach(
        function (field_info) {
          if (this.arch.attrs[field_info]) {
            try {
              this.loadParams[field_info] = JSON.parse(
                this.arch.attrs[field_info]
              );
              this.rendererParams[field_info] = JSON.parse(
                this.arch.attrs[field_info]
              );

              if (field_info == "ks_context") {
                let ks_context_info = JSON.parse(this.arch.attrs[field_info]);
                let ks_new_context = Object.assign(
                  {},
                  this.controllerParams.context,
                  ks_context_info
                );
                this.controllerParams.context = ks_new_context;
              }
              if (field_info == "ks_export_field") {
                this.rendererParams[field_info] = JSON.parse(
                  this.arch.attrs[field_info]
                );
                this.loadParams[field_info] = JSON.parse(
                  this.arch.attrs[field_info]
                );
                this.controllerParams[field_info] = JSON.parse(
                  this.arch.attrs[field_info]
                );
              }
            } catch (err) {
              console.error(err);
            }
            delete this.arch.attrs[field_info];
          }
        }.bind(this)
      );
    },

    /*
     * Function to return the gantt view attribute that is not the field, used for other purposes like
     * task linking info, gantt view configurations, etc.
     */
    ks_get_gantt_no_field_attribute: function () {
      return [
        "ks_task_link_info",
        "ks_gantt_config",
        "ks_context",
        "ks_export_field",
      ];
    },
  });
  view_registry.add("ks_gantt", KsGanttView);
  return KsGanttView;
});

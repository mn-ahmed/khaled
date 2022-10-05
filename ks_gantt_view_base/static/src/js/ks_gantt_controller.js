odoo.define("ks_gantt_view.Controller", function (require) {
  "use strict";

  var AbstractController = require("web.AbstractController");
  var core = require("web.core");
  var config = require("web.config");
  var QWeb = core.qweb;
  var _t = core._t;
  var dialogs = require("web.view_dialogs");
  var confirmDialog = require("web.Dialog").confirm;
  var framework = require("web.framework");

  var ksGanttController = AbstractController.extend({
    // Event to open create dialog modal.
    events: _.extend({}, AbstractController.prototype.events, {
      "click .ks_gantt_create_btn": "_ksCreateGantt",
      "click select#ks_gantt_view_zoom": "_ksOnClickView",
      "click select#ks_gantt_view_sort": "_ksSortGanttView",
      "click button.ks_current_time": "_ksCurrentTime",
      "click .ks_refresh_gantt": "_ksRefreshGantt",
      "click a.ks_gantt_export_list": "_ksExportReport",
      "click button#ks_toggle_fullscreen": "_ksFullScreen",
      "click .ks_gantt_grid_edit": "_ksTaskEdit",
      "click .ks_gantt_grid_delete": "_ksTaskDelete",
      "click .ks_gantt_grid_add": "_ksTaskAdd",
      "click .ks-resource-mode": "_ksResourceMode",
      "click button#ks_toggle_overlay": "_ksToggleOverlay",
      "click button#ks_toggle_no_of_days": "_ksToggleNoOfDays",
      "click button#ks_toggle_grid": "_ksToggleGrid",
      "click button#ks_toggle_resource": "_ksToggleResource",
      "click button#ks_zoom_to_fit": "_ksZoomToFit",
      "click button#ks_toggle_deadline": "_ksToggleDeadline",
      "click button#ks_critical_path": "_ksCriticalPath",
      "click button#ks_toggle_days_off": "_ksToggleDaysOff",
    }),

    init: function (parent, model, renderer, params) {
      this._super.apply(this, arguments);
      this.context = params.context;
      this.ks_dialogViews = params.ks_dialogViews;
      this.state = renderer.state;
      this.createAction = params.createAction;
      this.activeActions = params.activeActions;
      this.ks_params = params;
      this.ks_reload = false;
      this.ks_dialog_opened = false;
      this.ks_export_field = params.ks_export_field;
      // function to open task form view.
      gantt.showLightbox = function (id) {
        var self = this;
        var ksDialog = self._ksOpenDialog(id);
        if (ksDialog) {
          ksDialog.on("closed", this, function () {
            this.ks_reload = false;
            this.ks_dialog_opened = false;
          });
        }
      }.bind(this);

      // Gantt function to delete task.
      gantt.deleteTask = function (id) {
        if (this.model.modelName == gantt.ks_model_name) {
          this._KsDeleteTask(parseInt(id));
        }
      }.bind(this);

      gantt.$click.buttons.delete = function (id) {
        if (this.model.modelName == gantt.ks_model_name) {
          this._KsOnDeleteRecord(id);
        }
      }.bind(this);
    },

    custom_events: _.extend({}, AbstractController.prototype.custom_events, {
      ks_capsule_clicked: "ksOnCapsuleClicked",
      gantt_config: "ksGanttConfig",
      gantt_create_dp: "ksGanttCreateDp",
    }),

    ksGanttConfig: function () {
      var self = this;
      gantt.attachEvent("onBeforeLightbox", function (id) {
        // Leave blank this event to not render default task click.
      });

      gantt.attachEvent(
        "onBeforeLinkAdd",
        function (id, link) {
          // check linking from group_by task.
          if (
            this.modelName != "project.project" &&
            (!parseInt(link.source) || !parseInt(link.target))
          ) {
            gantt.message({
              type: "error",
              text: _t("You can't create link task with group"),
            });
            return false;
          }
          if (
            gantt.getTask(link.source).type == "project" ||
            gantt.getTask(link.target).type == "project" ||
            gantt.getTask(link.target).ks_group_lvl
          ) {
            gantt.message({
              type: "error",
              text: _t("You can't create link with project and group"),
            });
            return false;
          }
          return true;
        }.bind(this)
      );

      gantt.attachEvent(
        "onBeforeRowDragEnd",
        function (id, parent, target) {
          var task = gantt.getTask(id);
          var ks_task_update_task = {};
          var ks_all_task = gantt.serialize().data;
          var ks_init_sequence = 0;
          // if sequence present then update the sequence number for the task.
          for (var ks_task = 0; ks_task < ks_all_task.length; ks_task++) {
            ks_task_update_task[ks_all_task[ks_task].id] = {
              id: ks_all_task[ks_task].id,
            };
            if (ks_all_task[ks_task].ks_allow_subtask)
              ks_task_update_task[ks_all_task[ks_task].id].parent_id =
                ks_all_task[ks_task].parent;
            // init sequence number;
            if (ks_task == 0) {
              ks_init_sequence = ks_all_task[0].sequence;
            }

            if (ks_init_sequence >= ks_all_task[ks_task].sequence) {
              ks_init_sequence = ks_init_sequence + 1;
              ks_task_update_task[ks_all_task[ks_task].id]["sequence"] =
                ks_init_sequence;
            } else {
              ks_init_sequence = ks_all_task[ks_task].sequence;
            }
          }
          if (this.model.modelName == gantt.ks_model_name) {
            this.model
              .ksUpdateParentSequence(ks_task_update_task)
              .then(function (res) {
                // This is to update the state reload without render.
                gantt.ks_no_reload = true;
                self.reload();
              });
          }
          return true;
        }.bind(this)
      );

      // Event to check if the task can be moved or not.
      gantt.attachEvent("onBeforeRowDragMove", function (id, parent, tindex) {
        if (gantt.getTask(id).ks_allow_subtask) {
          return true;
        }
        return false;
      });
    },

    ksGanttCreateDp: function (event) {
      var self = this;
      this.ks_dp = gantt.createDataProcessor(function (
        entity,
        action,
        data,
        id
      ) {
        switch (action) {
          case "update":
            switch (entity) {
              case "task":
                if (self.model.modelName == gantt.ks_model_name) {
                  self.model.updateTask(data).then(
                    function (res) {
                      gantt.render();
                      // This is to update the state reload without render.
                      gantt.ks_no_reload = true;
                      self.reload();
                    },
                    function (reason) {
                      gantt.render();
                      self.reload();
                    }
                  );
                }
                break;
            }
            break;
          case "create":
            switch (entity) {
              case "link":
                // check for duplicate link.
                if (
                  _.where(gantt.config.ks_link_data, {
                    source: data.source,
                    target: data.target,
                  }).length
                ) {
                  break;
                }
                gantt.config.ks_link_data.push({
                  source: data.source,
                  target: data.target,
                });
                if (self.model.modelName == gantt.ks_model_name) {
                  self.model.ksCreateLink(data).then(function (res) {
                    gantt.ks_no_reload = true;
                    self.reload();
                    gantt.render();
                  });
                }
                break;
            }
            break;
          case "delete":
            switch (entity) {
              case "link":
                self.model.ksDeleteLink(data);
                let link_index = _.findLastIndex(gantt.config.ks_link_data, {
                  source: data.source,
                  target: data.target,
                });
                if (link_index > -1) {
                  gantt.config.ks_link_data.splice(link_index, 1);
                }
                gantt.ks_no_reload = true;
                self.reload();
                break;
            }
            break;
        }
      });
    },

    //render scale button
    renderButtons: function ($node) {
      // Render Create button.
      let values = {
        create: this.is_action_enabled("create"),
      };
      this.$buttons = $(
        QWeb.render("ks_gantt_view_base.control_panel_buttons", {
          values: values,
        })
      );
      if ($node) {
        this.$buttons.appendTo($node);
      }
    },

    start: async function () {
      const promises = [this._super()];
      await Promise.all(promises);
    },

    //Update the view on click of expand and collapse
    _update: function () {
      var self = this;
      if (this.ks_reload) {
        gantt.clearAll();
        this.renderer.ks_renderGantt();
        this.ks_reload = false;
        this.ks_dialog_opened = false;
      }
      return this._super.apply(this, arguments);
    },

    //on click of create
    ksOnCreate: function (context) {
      if (this.createAction) {
        var ks_contextData = _.extend({}, this.context, context);
        var ks_additionalContextData = {
          additional_context: ks_contextData,
          on_close: this.reload.bind(this, {}),
        };
        this.do_action(this.createAction, ks_additionalContextData);
      } else {
        this._ksOpenDialog(undefined, context);
      }
    },

    //Open Dialog for create and Edit and Delete
    _ksOpenDialog: function (KsresID, context) {
      var KsCapsuleModel = false;
      if (KsresID) {
        var ks_gantt_task = gantt.getTask(KsresID);
        if (ks_gantt_task && ks_gantt_task.ks_task_model) {
          KsresID = parseInt(KsresID.split("_")[1]);
          KsCapsuleModel = ks_gantt_task.ks_task_model;
        } else {
          KsresID = parseInt(KsresID);
        }
      } else if (
        context &&
        context.open_new_task_form &&
        (this.modelName == "project.task" ||
          this.modelName == "project.project")
      ) {
        KsCapsuleModel = "project.task";
      }

      // If KsresID is undefined then open create modal and KsresID have Integer value then open edit modal.
      // Otherwise click event triggered from the groupby parent task.
      if (KsresID != undefined && isNaN(KsresID)) {
        return false;
      }
      var self = this;
      this.ks_reload = true;
      this.ks_dialog_opened = true;
      if (KsresID) {
        var ks_title = _t("Edit");
      } else {
        var ks_title = _t("Create");
      }
      var Ks_data = {
        title: _.str.sprintf(ks_title),
        res_model: KsCapsuleModel ? KsCapsuleModel : self.modelName,
        view_id: self.ks_dialogViews[0][0],
        res_id: KsresID,
        readonly: !self.is_action_enabled("edit"),
        deletable: !(!self.is_action_enabled("edit") && KsresID),
        context: _.extend({}, self.context, context),
        on_saved: self.reload.bind(self, {}),
        on_remove: self._KsOnDeleteRecord.bind(self, KsresID),
      };
      return new dialogs.FormViewDialog(this, Ks_data).open();
    },

    // Handle task node event.
    ksOnCapsuleClicked: function (ev) {
      var self = this;
      var ks_state = ev.data.target;
      if (!this.ks_dialog_opened) {
        var ksDialog = self._ksOpenDialog(ks_state.attr("task_id"));
        if (ksDialog) {
          ksDialog.on("closed", this, function () {
            this.ks_reload = false;
            this.ks_dialog_opened = false;
          });
        }
      }
    },

    //On delete of record
    _KsOnDeleteRecord: function (KsRecordId) {
      var KsCapsuleModel = false;
      var ks_gantt_task = gantt.getTask(KsRecordId);
      if (ks_gantt_task && ks_gantt_task.ks_task_model) {
        KsRecordId = parseInt(KsRecordId.split("_")[1]);
        KsCapsuleModel = ks_gantt_task.ks_task_model;
      } else {
        KsRecordId = parseInt(KsRecordId);
      }
      var self = this;
      var ksDeleteConfirm = new Promise(function (resolve) {
        confirmDialog(this, _t("Are you sure to delete this record?"), {
          confirm_callback: function () {
            resolve(true);
          },
          cancel_callback: function () {
            resolve(false);
          },
        });
      });

      return ksDeleteConfirm.then(function (confirmed) {
        if (!confirmed) {
          return Promise.resolve();
        }
        var ksUnlinkData = {
          model: KsCapsuleModel ? KsCapsuleModel : self.modelName,
          method: "unlink",
          args: [[KsRecordId]],
        };
        return self._rpc(ksUnlinkData).then(function () {
          return self.reload();
        });
      });
    },

    _KsDeleteTask: function (id) {
      var ksUnlinkData = {
        model: this.modelName,
        method: "unlink",
        args: [[id]],
      };

      return this._rpc(ksUnlinkData).then(
        function () {
          return this.reload();
        }.bind(this)
      );
    },

    _ksFullScreen: function (ev) {
      gantt.ext.fullscreen.toggle();
      if (!gantt.config.ks_is_fullscreen) {
        // enable full screen / Expand the screen.
        gantt.config.ks_is_fullscreen = true;
        ev.currentTarget.classList.remove("fa-expand");
        ev.currentTarget.classList.add("fa-compress");
      } else {
        // collapse the screen.
        gantt.config.ks_is_fullscreen = false;
        ev.currentTarget.classList.remove("fa-compress");
        ev.currentTarget.classList.add("fa-expand");
      }
    },

    // Handle create button event.
    _ksCreateGantt: function () {
      this._ksOpenDialog();
    },

    _ksOnClickView: function (ev) {
      // Function to handle gantt view zoom level.
      // Disable graph overlay first.
      this.ks_disable_graph_overlay();
      gantt.ext.zoom.setLevel(ev.currentTarget.value);
    },

    _ksCurrentTime: function (ev) {
      // Scroll to the current date time.
      gantt.showDate(new Date());
    },

    _ksExportReport: function (ev) {
      ev.preventDefault();
      var ks_report_type = $(ev.currentTarget).attr("report_type");
      var ks_file_name =
        "gantt-chart-" +
        new Date()
          .toLocaleString()
          .replace(new RegExp("/", "g"), "-")
          .replace(new RegExp(", ", "g"), "-")
          .replace(new RegExp(":", "g"), "-");

      if (ks_report_type == "excel" && this.ks_export_field) {
        framework.blockUI();
        this.getSession().get_file({
          url: "/web/ksganttbase/export/xlsx",
          data: {
            ks_model_name: this.modelName,
            ks_fields: JSON.stringify(this.ks_export_field),
            ks_domain: JSON.stringify(this.model.domain),
            ks_context: JSON.stringify(this.context),
          },
          complete: framework.unblockUI,
          error: (error) => this.call("crash_manager", "rpc_error", error),
        });
      } else if (ks_report_type == "excel") {
        ks_file_name += ".xlsx";
        gantt.exportToExcel({
          name: ks_file_name,
          columns: [
            {
              id: "text",
              header: "Title",
            },
            {
              id: "start_date",
              header: "Start date",
            },
            {
              id: "end_date",
              header: "End date",
            },
          ],
        });
      } else if (ks_report_type == "pdf") {
        ks_file_name += ".pdf";
        gantt.exportToPDF({
          name: ks_file_name,
        });
      } else if (ks_report_type == "png") {
        ks_file_name += ".png";
        gantt.exportToPNG({
          name: ks_file_name,
        });
      } else if (ks_report_type == "json") {
        ks_file_name += ".json";
        gantt.exportToJSON({
          name: ks_file_name,
        });
      } else if (ks_report_type == "ms-project") {
        ks_file_name += ".xml";
        gantt.exportToMSProject({
          name: ks_file_name,
        });
      } else if (ks_report_type == "primaverap6") {
        ks_file_name += ".xml";
        gantt.exportToPrimaveraP6({
          name: ks_file_name,
          skip_circular_links: false,
        });
      } else if (ks_report_type == "ical") {
        ks_file_name += ".ical";
        gantt.exportToICal();
      } else {
        gantt.message({
          type: "warning",
          text: _t("Format not available"),
        });
      }
    },

    _ksTaskEdit: function (ev) {
      var task_id = ev.currentTarget.getAttribute("task_id");
      this._ksOpenDialog(task_id);
    },

    _ksTaskDelete: function (ev) {
      var task_id = ev.currentTarget.getAttribute("task_id");
      if (this.model.modelName == gantt.ks_model_name) {
        this._KsOnDeleteRecord(task_id);
      }
    },

    /*
     *   Handle add event on the gantt view grid panel.
     */
    _ksTaskAdd: function (ev) {
      var context = {};
      var task_id = ev.currentTarget.getAttribute("task_id");
      if (task_id) {
        var ks_gantt = gantt.getTask(task_id);
        if (ks_gantt.type == "project") {
          context["open_new_task_form"] = true;
          context["default_project_id"] = parseInt(task_id);
        } else {
          context["open_new_task_form"] = true;
          context["default_project_id"] = parseInt(ks_gantt.project_id);
          if (!context["default_project_id"] && this.context) {
            context["default_project_id"] = this.context.default_project_id;
          }
          if (parseInt(task_id).toString() == "NaN") {
            task_id = task_id.split("_")[1];
          }
          if (ks_gantt.ks_allow_subtask)
            context["default_parent_id"] = parseInt(task_id);
        }
      }
      this._ksOpenDialog(undefined, context);
    },

    _ksToggleOverlay: function (ev) {
      // Check if overlay is visible or not.
      var lineOverlay = gantt.config.lineOverlay;
      gantt.config.ks_overlay_result = true;
      if (gantt.ext.overlay.isOverlayVisible(lineOverlay)) {
        gantt.config.readonly = false;
        gantt.ext.overlay.hideOverlay(lineOverlay);
        gantt.$root.classList.remove("overlay_visible");
        this.ks_disable_button(ev);
      } else {
        gantt.config.readonly = true;
        gantt.ext.overlay.showOverlay(lineOverlay);
        gantt.$root.classList.add("overlay_visible");
        if (gantt.config.ks_overlay_result) {
          this.ks_enable_button(ev);
        } else {
          gantt.config.readonly = false;
          gantt.ext.overlay.hideOverlay(lineOverlay);
          gantt.$root.classList.remove("overlay_visible");
        }
      }

      // Check the current scale level of the view and set to again to work for graph overlay.
      var ks_current_scale_level = gantt.ext.zoom.getCurrentLevel();
      gantt.ext.zoom.setLevel(ks_current_scale_level);
    },

    _ksToggleNoOfDays: function (ev) {
      if (!gantt.config.ks_no_of_days) {
        gantt.config.ks_no_of_days = true;
        this.ks_enable_button(ev);
      } else {
        gantt.config.ks_no_of_days = false;
        this.ks_disable_button(ev);
      }
      gantt.render();
    },

    _ksToggleGrid: function (ev) {
      if (!gantt.config.ks_hide_grid_panel) {
        gantt.config.ks_hide_grid_panel = true;
        this.ks_enable_button(ev);
      } else {
        gantt.config.ks_hide_grid_panel = false;
        this.ks_disable_button(ev);
      }
      this.ks_disable_graph_overlay();
      this.renderer.ks_gantt_layout();
      this.renderer._render();
      gantt.resetLayout();
      gantt.addTaskLayer(gantt.config.ks_task_extra_info);
      gantt.render();
      if (document.getElementById("ks_toggle_overlay"))
        document.getElementById("ks_toggle_overlay").disabled = true;
    },

    _ksToggleResource: function (ev) {
      if (!gantt.config.ks_show_resource_panel) {
        gantt.config.ks_show_resource_panel = true;
        this.ks_enable_button(ev);
      } else {
        gantt.config.ks_show_resource_panel = false;
        this.ks_disable_button(ev);
      }

      this.ks_disable_graph_overlay();
      this.renderer.ks_gantt_layout();
      this.renderer._render();
      gantt.resetLayout();
      gantt.addTaskLayer(gantt.config.ks_task_extra_info);
      gantt.render();
      if (document.getElementById("ks_toggle_overlay"))
        document.getElementById("ks_toggle_overlay").disabled = true;
    },

    _ksResourceMode: function (ev) {
      gantt.config.ks_resource_mode = ev.currentTarget.value;
      gantt.render();
    },

    _ksZoomToFit: function () {
      function getUnitsBetween(from, to, unit, step) {
        var start = new Date(from),
          end = new Date(to);
        var units = 0;
        while (start.valueOf() < end.valueOf()) {
          units++;
          start = gantt.date.add(start, step, unit);
        }
        return units;
      }

      var project = gantt.getSubtaskDates(),
        areaWidth = gantt.$task.offsetWidth,
        scaleConfigs = gantt.ext.zoom._levels;

      for (var i = 0; i < scaleConfigs.length; i++) {
        var columnCount = getUnitsBetween(
          project.start_date,
          project.end_date,
          scaleConfigs[i].scales[scaleConfigs[i].scales.length - 1].unit,
          scaleConfigs[i].scales[0].step
        );
        if ((columnCount + 2) * gantt.config.min_column_width <= areaWidth) {
          break;
        }
      }

      if (i == scaleConfigs.length) {
        i = i - 2;
      }
      this.ks_disable_graph_overlay();
      gantt.ext.zoom.setLevel(scaleConfigs[i + 1].name);
    },

    _ksSortGanttView: function (ev) {
      var ks_selected_value = ev.currentTarget.value;
      if (ks_selected_value) {
        if (ks_selected_value == "name_sort_asc") {
          gantt.sort(sortTaskNameAsc);

          function sortTaskNameAsc(a, b) {
            a = a.text;
            b = b.text;
            return a > b ? 1 : a < b ? -1 : 0;
          }
        } else if (ks_selected_value == "name_sort_desc") {
          gantt.sort(sortTaskNameDesc);

          function sortTaskNameDesc(a, b) {
            a = a.text;
            b = b.text;
            return a < b ? 1 : a > b ? -1 : 0;
          }
        } else if (ks_selected_value == "create_sort_asc") {
          gantt.sort(sortTaskCreateAsc);

          function sortTaskCreateAsc(a, b) {
            a = a.create_date;
            b = b.create_date;
            return a > b ? 1 : a < b ? -1 : 0;
          }
        } else if (ks_selected_value == "create_sort_desc") {
          gantt.sort(sortTaskCreateDesc);

          function sortTaskCreateDesc(a, b) {
            a = a.create_date;
            b = b.create_date;
            return a < b ? 1 : a > b ? -1 : 0;
          }
        } else if (ks_selected_value == "create_duration_asc") {
          gantt.sort(sortTaskDurationAsc);

          function sortTaskDurationAsc(a, b) {
            a = a.end_date - a.start_date;
            b = b.end_date - b.start_date;
            return a > b ? 1 : a < b ? -1 : 0;
          }
        } else if (ks_selected_value == "create_duration_desc") {
          gantt.sort(sortTaskDurationDesc);

          function sortTaskDurationDesc(a, b) {
            a = a.end_date - a.start_date;
            b = b.end_date - b.start_date;
            return a < b ? 1 : a > b ? -1 : 0;
          }
        } else {
          this.renderer.ks_gantt_layout();
          this.renderer._render();
        }
      }
    },

    _ksToggleDeadline: function (ev) {
      if (!gantt.config.ks_toggle_deadline) {
        gantt.config.ks_toggle_deadline = true;
        this.ks_enable_button(ev);
      } else {
        gantt.config.ks_toggle_deadline = false;
        this.ks_disable_button(ev);
      }
      this.renderer.ks_gantt_layout();
      this.renderer._render();
    },

    _ksCriticalPath: function (ev) {
      if (!gantt.config.highlight_critical_path) {
        gantt.config.highlight_critical_path = true;
        this.ks_enable_button(ev);
      } else {
        gantt.config.highlight_critical_path = false;
        this.ks_disable_button(ev);
      }
      gantt.render();
    },

    _ksToggleDaysOff: function (ev) {
      if (!gantt.config.ks_enable_days_off) {
        gantt.config.ks_enable_days_off = true;
        this.ks_enable_button(ev);
      } else {
        gantt.config.ks_enable_days_off = false;
        this.ks_disable_button(ev);
      }
      gantt.render();
    },

    ks_enable_button: function (ev) {
      $(ev.currentTarget).addClass("ks_control_active");
    },

    ks_disable_button: function (ev) {
      $(ev.currentTarget).removeClass("ks_control_active");
    },

    ks_disable_graph_overlay: function () {
      var lineOverlay = gantt.config.lineOverlay;
      if (gantt.ext.overlay.isOverlayVisible(lineOverlay)) {
        gantt.config.readonly = false;
        gantt.ext.overlay.hideOverlay(lineOverlay);
        gantt.$root.classList.remove("overlay_visible");
        $("#ks_toggle_overlay").removeClass("ks_control_active");
      }
    },

    destroy: function () {
      // destroy gantt view createDataProcessor
      this.ks_dp.destructor();
      this.ks_dp.ks_dp = false;
      this._super.apply(this, arguments);
    },

    ks_disable_resource_panel: function () {
      // Hide resource panel.
      gantt.config.ks_show_resource_panel = false;
      $("button#ks_toggle_resource").removeClass("ks_control_active");
    },

    reload: function (params) {
      // check if resource panel is active then close it first.
      this.ks_disable_resource_panel();
      return this._super.apply(this, arguments);
    },

    _ksRefreshGantt: function () {
      this.reload();
    },
  });

  return ksGanttController;
});

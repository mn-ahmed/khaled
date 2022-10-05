odoo.define("ks_gantt_view.Renderer", function (require) {
  "use strict";

  var AbstractRenderer = require("web.AbstractRenderer");
  var qweb = require("web.QWeb");
  var core = require("web.core");
  var GanttModel = require("ks_gantt_view.Model");
  var QWeb = core.qweb;
  var _t = core._t;
  var ajax = require("web.ajax");
  var session = require("web.session");
  var time = require("web.time");

  var ksGanttRenderer = AbstractRenderer.extend({
    template: "ks_gantt_view_base.ks_gantt_content",

    _KsTaskClicked: function (ev) {
      ev.preventDefault();
      this.trigger_up("ks_capsule_clicked", {
        target: $(ev.currentTarget),
      });
    },

    /**
     * Initialise gantt view.
     */
    init: function (parent, state, params) {
      var self = this;
      this._super.apply(this, arguments);
      this.ks_gantt_rendered = false;
      this.ks_gantt_config = params.ks_gantt_config;
      this.ks_isCreate = params.ks_isCreate;
      this.ks_isEdit = params.ks_isEdit;
      this.ks_no_drag = params.ks_no_drag;
      this.ks_hide_links = params.ks_hide_links;
      this.ks_fieldDetail = params.ks_fieldDetail;
      this.string = params.string;
      this.ks_model_name = params.ks_model_name;
      gantt.ks_model_name = params.ks_model_name;
      this.active_id = params.active_id;
      this.ks_gantt_arch = params.ks_gantt_arch;
      gantt.config.grid_resize = true;
      gantt.config.date_grid = "%d/%m/%Y %h:%i";

      // Left grid columns with buttons.
      this.ks_left_grid_columns();

      // Change gantt view scale drop-down.
      this.ks_set_scale_dropdown();

      // Add export field details
      this.ks_export_field = params.ks_export_field;

      // Initialize gantt view scale level.
      gantt.ext.zoom.init(this.ks_zoom_config());
      // Default scale level.
      gantt.ext.zoom.setLevel("day");
      gantt.config.duration_unit = "hour";

      // Disable gantt view default lightbox popup to create new task.
      gantt.attachEvent(
        "onTaskCreated",
        function (task) {
          return false;
        }.bind(this)
      );
    },

    /**
     * On attach callback is used because gantt view library needs the html element to render.
     */
    on_attach_callback: function () {
      this._super();
      this.ks_renderGantt();
      this.ks_gantt_rendered = true;
      gantt.showDate(new Date());
    },

    /**
     * Render gantt view.
     */
    ks_renderGantt: function () {
      var self = this;
      // List of attached events for the gantt view, so we can de-attach the events after the view gets destroy.
      gantt.config.ks_attached_events = [];

      var range = gantt.getSubtaskDates();
      var end_date = new Date();
      end_date.setDate(end_date.getDate() + 4);

      // Initialize the gantt view.
      gantt.config.ks_link_data = [];
      gantt.config.drag_project = true;
      gantt.config.drag_resize = true;
      gantt.config.show_links = true;
      gantt.config.sort = true;

      self.ks_gantt_plugins();

      gantt.config.auto_scheduling = true;
      gantt.config.keyboard_navigation_cells = true;

      this.ks_handle_critical_tasks();

      gantt.ks_project_settings = {};

      // Check settings gantt view feature settings is enable from project settings or not.
      if (
        this.ks_enable_task_dynamic_text === undefined ||
        this.ks_enable_task_dynamic_text
      ) {
        this.ks_enable_task_dynamic_text = true;
        gantt.ks_project_settings["ks_enable_task_dynamic_text"] = true;
      }

      this.ks_select_columns();

      // Manage task ordering.
      this.ks_task_drag_and_drop();

      this.ks_handle_non_working_timeline();
      this.ks_handle_group_by_text();

      this.trigger_up("gantt_config");
      this.trigger_up("gantt_create_dp");

      // Set gantt view height.
      var ks_extra_space =
        $(".o_main_navbar").height() +
        $(".o_control_panel").height() +
        $(".ks_gantt_right_control").height();
      this.$(".ks_gantt_view_content").height(
        window.outerHeight - ks_extra_space
      );

      this.ks_handle_task_side_content();

      gantt.config.ks_project_tooltip_config = this.ks_project_tooltip_config;

      // function to manages tooltip of the task.
      gantt.templates.tooltip_text = function (start, end, task) {
        var ks_tooltip_text = "";

        // Task Name
        if (gantt.config.ks_project_tooltip_config) {
          if (gantt.config.ks_project_tooltip_config.ks_tooltip_task_name) {
            ks_tooltip_text +=
              "<b>" + _t("Title : ") + "</b> " + task.text + "<br/>";
          }
        } else {
          ks_tooltip_text +=
            "<b>" + _t("Title : ") + "</b> " + task.text + "<br/>";
        }

        // Task duration
        if (gantt.config.ks_project_tooltip_config) {
          if (gantt.config.ks_project_tooltip_config.ks_tooltip_task_duration) {
            if (task.ks_task_duration) {
              ks_tooltip_text +=
                "<b>" +
                _t("Duration :") +
                "</b> " +
                task.ks_task_duration +
                " <br/>";
            } else {
              ks_tooltip_text +=
                "<b>" +
                _t("Duration :") +
                "</b> " +
                task.ks_task_difference +
                "<br/>";
            }
          }
        } else {
          if (task.ks_task_duration) {
            ks_tooltip_text +=
              "<b>" +
              _t("Duration :") +
              "</b> " +
              task.ks_task_duration +
              " <br/>";
          } else {
            ks_tooltip_text +=
              "<b>" +
              _t("Duration :") +
              "</b> " +
              task.ks_task_difference +
              "<br/>";
          }
        }

        // Task start date
        if (gantt.config.ks_project_tooltip_config) {
          if (
            gantt.config.ks_project_tooltip_config.ks_tooltip_task_start_date
          ) {
            ks_tooltip_text +=
              "<b>" +
              _t("Start Date : ") +
              "</b> " +
              gantt.ks_gantt_view_datetime_format(task.start_date) +
              "<br/>";
          }
        } else {
          ks_tooltip_text +=
            "<b>" +
            _t("Start Date : ") +
            "</b> " +
            gantt.ks_gantt_view_datetime_format(task.start_date) +
            "<br/>";
        }

        // Task end date
        if (gantt.config.ks_project_tooltip_config) {
          if (gantt.config.ks_project_tooltip_config.ks_tooltip_task_end_date) {
            ks_tooltip_text +=
              "<b>" +
              _t("End Date : ") +
              "</b> " +
              gantt.ks_gantt_view_datetime_format(task.end_date) +
              "<br/>";
          }
        } else {
          ks_tooltip_text +=
            "<b>" +
            _t("End Date : ") +
            "</b> " +
            gantt.ks_gantt_view_datetime_format(task.end_date) +
            "<br/>";
        }

        // Task Stage Id
        if (
          gantt.config.ks_project_tooltip_config &&
          ["task", "milestone"].includes(task.type)
        ) {
          if (gantt.config.ks_project_tooltip_config.ks_tooltip_task_stage) {
            ks_tooltip_text +=
              "<b>" +
              _t("Stage : ") +
              "</b> " +
              (task.stage_id ? task.stage_id[1] : task.stage_id) +
              "<br/>";
          }
        } else if (["task", "milestone"].includes(task.type)) {
          ks_tooltip_text +=
            "<b>" +
            _t("Stage : ") +
            "</b> " +
            (task.stage_id ? task.stage_id[1] : task.stage_id) +
            "<br/>";
        } else if (
          !task.type &&
          gantt.config.ks_project_tooltip_config &&
          gantt.config.ks_project_tooltip_config.ks_tooltip_task_stage
        ) {
          ks_tooltip_text +=
            "<b>" +
            _t("Stage : ") +
            "</b> " +
            (task.stage_id ? task.stage_id : false) +
            "<br/>";
        }

        // Task Deadline
        if (
          gantt.config.ks_project_tooltip_config &&
          ["task", "milestone"].includes(task.type)
        ) {
          if (
            gantt.config.ks_project_tooltip_config.ks_tooltip_task_deadline &&
            task.ks_deadline_tooltip
          ) {
            ks_tooltip_text +=
              "<b>" +
              _t("Deadline : ") +
              "</b> " +
              gantt.ks_gantt_view_datetime_format(task.ks_deadline_tooltip) +
              "<br/>";
          }
        } else if (
          task.ks_deadline_tooltip &&
          ["task", "milestone"].includes(task.type)
        ) {
          ks_tooltip_text +=
            "<b>" +
            _t("Deadline : ") +
            "</b> " +
            gantt.ks_gantt_view_datetime_format(task.ks_deadline_tooltip) +
            "<br/>";
        }

        // Task Progress
        if (
          gantt.config.ks_project_tooltip_config &&
          ["task", "milestone"].includes(task.type)
        ) {
          if (gantt.config.ks_project_tooltip_config.ks_tooltip_task_progress) {
            ks_tooltip_text +=
              "<b>" +
              _t("Progress : ") +
              "</b> " +
              Math.round(task.progress * 100) +
              "%" +
              "<br/>";
          }
        } else if (["task", "milestone"].includes(task.type)) {
          ks_tooltip_text +=
            "<b>" +
            _t("Progress : ") +
            "</b> " +
            Math.round(task.progress * 100) +
            "%" +
            "<br/>";
        } else if (
          !task.type &&
          gantt.config.ks_project_tooltip_config &&
          gantt.config.ks_project_tooltip_config.ks_tooltip_task_progress
        ) {
          ks_tooltip_text +=
            "<b>" +
            _t("Progress : ") +
            "</b> " +
            Math.round(task.progress * 100) +
            "%" +
            "<br/>";
        }

        // Task Constraint Type
        if (
          gantt.config.ks_project_tooltip_config &&
          ["task", "milestone"].includes(task.type)
        ) {
          if (
            gantt.config.ks_project_tooltip_config
              .ks_tooltip_task_constraint_type
          ) {
            ks_tooltip_text +=
              "<b>" +
              _t("Constraint Type : ") +
              "</b> " +
              gantt.locale.labels[task.constraint_type] +
              "<br/>";
          }
        } else if (["task", "milestone"].includes(task.type)) {
          ks_tooltip_text +=
            "<b>" +
            _t("Constraint Type : ") +
            "</b> " +
            gantt.locale.labels[task.constraint_type] +
            "<br/>";
        } else if (
          !task.type &&
          gantt.config.ks_project_tooltip_config &&
          gantt.config.ks_project_tooltip_config.ks_tooltip_task_constraint_type
        ) {
          ks_tooltip_text +=
            "<b>" +
            _t("Constraint Type : ") +
            "</b> " +
            gantt.locale.labels[task.constraint_type] +
            "<br/>";
        }

        // Task Constraint Date
        if (
          task.constraint_date &&
          !["asap", "alap"].includes(task.constraint_type)
        ) {
          if (
            gantt.config.ks_project_tooltip_config &&
            ["task", "milestone"].includes(task.type)
          ) {
            if (
              gantt.config.ks_project_tooltip_config
                .ks_tooltip_task_constraint_date &&
              task.constraint_date &&
              ["asap", "alap"].indexOf(task.constraint_type) < 0
            ) {
              ks_tooltip_text +=
                "<b>" +
                _t("Constraint Date : ") +
                "</b> " +
                gantt.ks_gantt_view_datetime_format(task.constraint_date) +
                "<br/>";
            }
          } else if (
            task.constraint_date &&
            ["asap", "alap"].indexOf(task.constraint_type) < 0 &&
            ["task", "milestone"].includes(task.type)
          ) {
            ks_tooltip_text +=
              "<b>" +
              _t("Constraint Date : ") +
              "</b> " +
              gantt.ks_gantt_view_datetime_format(task.constraint_date) +
              "<br/>";
          } else if (
            !task.type &&
            gantt.config.ks_project_tooltip_config &&
            gantt.config.ks_project_tooltip_config
              .ks_tooltip_task_constraint_date
          ) {
            ks_tooltip_text +=
              "<b>" +
              _t("Constraint Date : ") +
              "</b> " +
              gantt.ks_gantt_view_datetime_format(task.constraint_date) +
              "<br/>";
          }
        }

        return ks_tooltip_text;
      };

      // Add deadline for new task.
      gantt.config.ks_attached_events.push(
        gantt.attachEvent("onTaskLoading", function (task) {
          if (task.deadline) task.deadline = moment(task.deadline).toDate();
          return true;
        })
      );

      // Task quick info.
      self.ks_task_quick_info();

      // Gantt view linked task.
      self.ks_linked_task_info();

      // Gantt view dynamic task content.
      self.ks_task_dynamic_content();

      // Enable/disable dynamic progress
      gantt.config.ks_task_dynamic_progress = false;
      if (
        this.ks_enable_task_dynamic_progress == undefined ||
        this.ks_enable_task_dynamic_progress
      ) {
        gantt.config.ks_task_dynamic_progress = true;
      }

      if (this.ks_days_off) {
        gantt.config.ks_days_off_selection = this.ks_days_off_selection;
        gantt.config.ks_days_off = this.ks_days_off;
        gantt.config.ks_hide_date = this.ks_hide_date;
      }
      gantt.config.ks_exclude_holiday = this.ks_exclude_holiday;
      if (gantt.config.ks_exclude_holiday) {
        self.ks_exclude_holiday_function();
      }
      self.ks_days_off_func();

      // Manage gantt view layout.
      self.ks_gantt_layout();
      gantt.config.ks_resource_panel_render = false;
      if (gantt.config.ks_show_resource_panel) self.ks_resource_panel();
      // Enable smart rendering for gantt view.
      gantt.config.smart_rendering = true;
      gantt.config.ks_is_fullscreen = false;
      gantt.config.ks_gantt_task_data = this.ks_parse_gantt_data();

      // set full screen element.
      this.ks_full_screen_element();
      this.ks_control_panel_slider();

      // Manage datetime format.
      this.ks_gantt_view_datetime_format();
      gantt.config.show_unscheduled = true;
      if ($(".oe_dashboard").length) {
        $("#ks_toggle_fullscreen").css("display", "none");
        gantt.config.autosize = "y";
      } else {
        gantt.config.autosize = false;
      }

      gantt.init(this.$(".ks_gantt_view_content").get(0));
      //            if (gantt.config.ks_show_resource_panel && gantt.config.ks_owner_task_list) {
      //                gantt.config.ks_resources_store.parse(gantt.config.ks_owner_task_list);
      //            }
      if (gantt.config.ks_render_count) {
        gantt.clearAll();
        gantt.config.ks_disable_graph_overlay = true;
      }
      gantt.config.ks_render_count = true;
      gantt.parse(gantt.config.ks_gantt_task_data);
      // Add markers
      this.ks_handle_gantt_view_marker();
      gantt.addTaskLayer(gantt.config.ks_task_extra_info);
      gantt.render();
      this.ks_disable_control_panel_buttons();
      // gantt view overlay.
      this.ks_gantt_overlay_canvas();

      // Event to stop drag task if user don't have the permission for edit and task is in auto mode.
      gantt.config.ks_attached_events.push(
        gantt.attachEvent(
          "onBeforeTaskDrag",
          function (id, mode, e) {
            // Do not move group by task.
            if (gantt.getTask(id).type == "project") return false;
            if (this.ks_no_drag) return false;

            if (gantt.getTask(id).ks_task_no_drag) {
              return false;
            }

            if (
              !this.ks_isEdit ||
              gantt.getTask(id).ks_schedule_mode == "auto"
            ) {
              return false;
            }
            return true;
          }.bind(self)
        )
      );
    },

    /**
     * ks_parse_gantt_data - Function to create dictionary to render the data
     * on the gantt view.
     * @return {type}  render dictionary
     */
    ks_parse_gantt_data: function () {
      var ks_render_data = {};
      var ks_data = [];
      var ks_links = [];
      var ks_gantt_fields = this.ks_gantt_arch;

      // Check for grouped data if not found then render task without grouped.
      if (!this.state.groupedBy.length) {
        this.state.records.forEach(
          function (each_task) {
            this.ks_data_update(
              each_task,
              ks_links,
              ks_data,
              ks_gantt_fields,
              false
            );
            if (each_task.ks_project_task_json) {
              var ks_project_task_data = JSON.parse(
                each_task.ks_project_task_json
              );
              ks_project_task_data.forEach(
                function (each_project_task) {
                  this.ks_project_task_data_update(
                    each_project_task,
                    ks_links,
                    ks_data,
                    each_task.id
                  );
                }.bind(this)
              );
            }
          }.bind(this)
        );
      }
      // If Grouped data is available then render data with group by.
      if (this.state.groupedBy.length) {
        return this.ks_render_data_group_by();
      }

      ks_render_data["data"] = ks_data;
      ks_render_data["links"] = ks_links;
      return ks_render_data;
    },

    // Function to render group by task.
    ks_render_data_group_by: function () {
      var ks_data = [];
      var ks_links = [];
      var ks_render_data = {};
      var ks_id_list = [];
      var ks_gantt_fields = this.ks_gantt_arch;
      if (this.state.ks_group_by_records) {
        for (var group_index in this.state.ks_group_by_records) {
          var parent_group_id = 0;
          var ks_group_by_dict = {};
          var each_group = this.state.ks_group_by_records[group_index];
          // Multi level group-by
          // This will create a hierarchy for multi level group-by and have parent id for data.
          for (var group_lvl in this.state.groupedBy) {
            var sub_group_name = this.state.groupedBy[group_lvl];
            var ks_each_group_sub_group = this.state.groupedBy[group_lvl];

            var sub_group;
            var sub_group_id;
            // First group is normal
            if (parseInt(group_lvl) < 1) {
              if (each_group[ks_each_group_sub_group])
                sub_group = Array.isArray(each_group[ks_each_group_sub_group])
                  ? each_group[ks_each_group_sub_group]
                  : each_group[ks_each_group_sub_group].toString();
              // Check if field type is selection
              if (this.ks_fieldDetail[sub_group_name].type == "selection") {
                sub_group = this.ks_get_stage_data(sub_group_name, sub_group);
              }
              if (sub_group) {
                ks_data.push({
                  id:
                    "group_" +
                    (typeof sub_group == "string" ? sub_group : sub_group[0]),
                  text: typeof sub_group == "string" ? sub_group : sub_group[1],
                  parent: parent_group_id,
                  ks_group_lvl: 1,
                  type: "project",
                  open: true,
                });
                parent_group_id =
                  "group_" +
                  (typeof sub_group == "string" ? sub_group : sub_group[0]);
                ks_id_list.push(
                  "group_" +
                    (typeof sub_group == "string" ? sub_group : sub_group[0])
                );
              }
            }
            // Sub-group needs to be changed its ids to stop duplicate id.
            if (parseInt(group_lvl) > 0) {
              if (each_group[ks_each_group_sub_group])
                sub_group = Array.isArray(each_group[ks_each_group_sub_group])
                  ? each_group[ks_each_group_sub_group][1]
                  : each_group[ks_each_group_sub_group].toString();
              sub_group_id = Array.isArray(each_group[ks_each_group_sub_group])
                ? each_group[ks_each_group_sub_group][0]
                : each_group[ks_each_group_sub_group].toString();
              // Check if field type is selection
              if (this.ks_fieldDetail[sub_group_name].type == "selection") {
                sub_group = this.ks_get_stage_data(
                  ks_each_group_sub_group,
                  sub_group
                );
              }
              if (sub_group) {
                var new_id =
                  parent_group_id +
                  "_" +
                  sub_group[0] +
                  "_" +
                  sub_group_id.toString();
                ks_data.push({
                  id: new_id,
                  text: sub_group,
                  parent: parent_group_id,
                  ks_group_lvl: 1,
                  open: true,
                });
                ks_id_list.push(new_id);
                parent_group_id = new_id;
              }
            }

            if (sub_group) ks_group_by_dict[sub_group_name] = sub_group;
          }
          // From here needs to filter out data according for groups.
          for (var ks_task_index in this.state.records) {
            var ks_each_task = this.state.records[ks_task_index];
            var ks_render_check = true;

            for (var ks_check_group_index in ks_group_by_dict) {
              var ks_check_group = ks_group_by_dict[ks_check_group_index];
              //                            if (JSON.stringify(ks_check_group) != JSON.stringify(ks_each_task[ks_check_group_index])) {
              //                                ks_render_check = false;
              //                            }
            }
            //                        if (this.state.groupedBy[group_lvl]==='user_ids'){
            // var ks_parent = 0
            // if (ks_each_task['ks_user_ids']) {
            //     var ks_iterators = JSON.parse(ks_each_task['ks_user_ids'].replace(/'/g, '"'));
            // }

            // Assign data with to its group.
            if (
              this.ks_compare_group_by_data(
                ks_each_task[sub_group_name],
                each_group[sub_group_name]
              )
            ) {
              if (!ks_id_list.includes(ks_each_task.id)) {
                this.ks_data_update(
                  ks_each_task,
                  ks_links,
                  ks_data,
                  ks_gantt_fields,
                  parent_group_id
                );
                ks_id_list.push(ks_each_task.id);
              }
              if (ks_each_task.ks_project_task_json) {
                var ks_project_task_data = JSON.parse(
                  ks_each_task.ks_project_task_json
                );
                ks_project_task_data.forEach(
                  function (each_project_task) {
                    this.ks_project_task_data_update(
                      each_project_task,
                      ks_links,
                      ks_data,
                      ks_each_task.id
                    );
                  }.bind(this)
                );
              }
            }
            //                            for (var i in ks_iterators){
            // if (this.ks_compare_group_by_data(ks_each_task[ks_each_group_sub_group], each_group[ks_each_group_sub_group])) {
            //     if (ks_iterators) {
            //         if (this.state.groupedBy[group_lvl] === 'user_ids' || parseInt(group_lvl) < 1) {
            //             if (ks_iterators.length > 1 && !ks_id_list.includes(ks_each_task.id)) {
            //                 var tem_id = ''
            //                 var ks_text = []
            //                 for (var ks_id in ks_iterators) {
            //                     var ks_group_id = "group_" + ks_iterators[ks_id][0].toString()
            //                     var tem_id = ks_group_id + tem_id
            //                     var ks_temp_text = ks_text.push(ks_iterators[ks_id][1])
            //                 }
            //                 ks_data.push({
            //                     'id': tem_id,
            //                     'text': ks_text,
            //                     'parent': ks_parent,
            //                     'ks_group_lvl': 1,
            //                     'type': 'project',
            //                     'open': true
            //                 });
            //                 ks_parent = tem_id,
            //                     ks_id_list.push(tem_id);

            //             }

            //         }
            //         if (parseInt(group_lvl) > 0 && !ks_id_list.includes(ks_each_task.id)) {
            //             if (each_group[ks_each_group_sub_group])
            //                 sub_group = Array.isArray(each_group[ks_each_group_sub_group]) ? each_group[ks_each_group_sub_group][1] : each_group[ks_each_group_sub_group].toString();
            //             sub_group_id = Array.isArray(each_group[ks_each_group_sub_group]) ? each_group[ks_each_group_sub_group][0] : each_group[ks_each_group_sub_group].toString();
            //             // Check if field type is selection
            //             if (this.ks_fieldDetail[sub_group_name].type == 'selection') {
            //                 sub_group = this.ks_get_stage_data(ks_each_group_sub_group, sub_group);
            //             }
            //             if (sub_group) {
            //                 var new_id = ks_parent + "_" + sub_group[0] + "_" + sub_group_id.toString();
            //                 ks_data.push({
            //                     'id': new_id,
            //                     'text': sub_group,
            //                     'parent': ks_parent,
            //                     'ks_group_lvl': 1,
            //                     'open': true
            //                 });
            //                 ks_id_list.push(new_id);
            //                 ks_parent = new_id;
            //             }
            //         }
            //         if (!ks_id_list.includes(ks_each_task.id) && ks_iterators.length == 1 && this.state.groupedBy[group_lvl] === 'user_ids') {
            //             this.ks_data_update(ks_each_task, ks_links, ks_data, ks_gantt_fields, parent_group_id);
            //             ks_id_list.push(ks_each_task.id)

            //         }
            //         else if (!ks_id_list.includes(ks_each_task.id) && ks_iterators.length > 1 && this.state.groupedBy[group_lvl] === 'user_ids') {
            //             this.ks_data_update(ks_each_task, ks_links, ks_data, ks_gantt_fields, ks_parent);
            //             ks_id_list.push(ks_each_task.id)

            //         } else if (!ks_id_list.includes(ks_each_task.id) && parseInt(group_lvl) > 0) {
            //             this.ks_data_update(ks_each_task, ks_links, ks_data, ks_gantt_fields, ks_parent);
            //             ks_id_list.push(ks_each_task.id)
            //         }
            //         else {
            //             if (this.ks_compare_group_by_data(ks_each_task[ks_each_group_sub_group], each_group[ks_each_group_sub_group])) {
            //                 if (!ks_id_list.includes(ks_each_task.id)) {
            //                     this.ks_data_update(ks_each_task, ks_links, ks_data, ks_gantt_fields, parent_group_id);
            //                     ks_id_list.push(ks_each_task.id);

            //                 }
            //             }
            //         }
            //     }

            //     if (ks_each_task.ks_project_task_json) {
            //         var ks_project_task_data = JSON.parse(ks_each_task.ks_project_task_json);
            //         ks_project_task_data.forEach(function (each_project_task) {
            //             this.ks_project_task_data_update(each_project_task, ks_links, ks_data, ks_each_task.id);
            //         }.bind(this));
            //     }
            // }
          }
        }
      }
      ks_render_data["data"] = ks_data;
      ks_render_data["links"] = ks_links;
      return ks_render_data;
    },

    /*
     * Function to compare/match record data with applied group by to make the record its child.
     */
    ks_compare_group_by_data: function (ks_applied_grouped, ks_current_record) {
      if (ks_applied_grouped && ks_current_record) {
        for (
          var ks_index = 0;
          ks_index < ks_current_record.length;
          ks_index++
        ) {
          if (ks_applied_grouped[ks_index] != ks_current_record[ks_index])
            return false;
          return true;
        }
      }
    },

    willStart: function () {
      var self = this;
      var ksGetTheme = this._rpc({
        model: "res.config.settings",
        method: "ks_gantt_view_theme",
      }).then(function (result) {
        // Apply library theme css files.
        if (!result.ks_gantt_view_theme)
          result.ks_gantt_view_theme = "dhtmlxgantt_terrace.css";
        var ks_gantt_lib_theme =
          "/ks_gantt_view_base/static/lib/gantt_7.0.11_commercial/codebase/skins/" +
          result.ks_gantt_view_theme;
        ajax.loadCSS(ks_gantt_lib_theme);

        // Apply custom theme css files.
        if (result.ks_gantt_view_theme == "dhtmlxgantt_meadow.css") {
          ajax.loadCSS(
            "/ks_gantt_view_base/static/src/css/skins/ks_meadow.css"
          );
        }
        if (result.ks_gantt_view_theme == "dhtmlxgantt_broadway.css") {
          ajax.loadCSS(
            "/ks_gantt_view_base/static/src/css/skins/ks_broadway.css"
          );
        }
        if (result.ks_gantt_view_theme == "dhtmlxgantt_material.css") {
          ajax.loadCSS(
            "/ks_gantt_view_base/static/src/css/skins/ks_material.css"
          );
        }
        if (result.ks_gantt_view_theme == "dhtmlxgantt_contrast_white.css") {
          ajax.loadCSS(
            "/ks_gantt_view_base/static/src/css/skins/ks_contrast-white.css"
          );
        }
        if (result.ks_gantt_view_theme == "dhtmlxgantt_contrast_black.css") {
          ajax.loadCSS(
            "/ks_gantt_view_base/static/src/css/skins/ks_contrast-black.css"
          );
        }
        if (result.ks_gantt_view_theme == "dhtmlxgantt_terrace.css") {
          ajax.loadCSS(
            "/ks_gantt_view_base/static/src/css/skins/ks_terrace.css"
          );
        }

        // Enable/Disable RTL of the gantt view.
        if (result.ks_gantt_rtl == "True") {
          gantt.config.rtl = true;
        } else {
          gantt.config.rtl = false;
        }
      });
      return Promise.all([this._super.apply(this, arguments), ksGetTheme]);
    },

    // override render function to render gantt chart.
    _render: function () {
      Promise.resolve();
      if (gantt.ks_no_reload) {
        gantt.ks_no_reload = false;
        return false;
      }
      if (this.ks_gantt_rendered) {
        gantt.clearAll();
        this.ks_task_drag_and_drop();
        //                if (gantt.config.ks_show_resource_panel)
        //                    this.ks_resource_panel();
        delete gantt.config.ks_owner_task_list;
        gantt.config.ks_gantt_task_data = this.ks_parse_gantt_data();
        gantt.config.counter = true;
        if (
          gantt.config.ks_show_resource_panel &&
          gantt.config.ks_owner_task_list &&
          gantt.config.counter
        ) {
          gantt.config.ks_resources_store.parse(
            gantt.config.ks_owner_task_list
          );
          gantt.config.counter = false;
        }
        gantt.parse(gantt.config.ks_gantt_task_data);
        // Add markers
        this.ks_handle_gantt_view_marker();
      }
    },

    /**
     *
     *  Function to update gantt data dictionary
     *
     */
    ks_data_update: function (
      each_task,
      ks_links,
      ks_data,
      ks_gantt_fields,
      parent_group_id
    ) {
      if (each_task[ks_gantt_fields.ks_task_link]) {
        JSON.parse(each_task[ks_gantt_fields.ks_task_link]).forEach(
          (item, index) => {
            ks_links.push({
              id: item.id,
              source: item.source,
              target: item.target,
              type: item.type,
            });
            gantt.config.ks_link_data.push({
              id: item.id,
              source: item.source,
              target: item.target,
              type: item.type,
            });
          }
        );
      }

      var ks_resource_hours_available = {};
      if (each_task[ks_gantt_fields.ks_resource_hours_available])
        ks_resource_hours_available = JSON.parse(
          each_task[ks_gantt_fields.ks_resource_hours_available]
        );

      // Update task type.
      var ks_task_type = each_task[ks_gantt_fields.ks_task_type];
      if (ks_gantt_fields.ks_project_row) {
        ks_task_type = "project";
      }
      var ks_gantt_data = {
        id: each_task[ks_gantt_fields.ks_task_id],
        text: each_task[ks_gantt_fields.ks_task_name],
        color: each_task[ks_gantt_fields.ks_task_color]
          ? each_task[ks_gantt_fields.ks_task_color]
          : "#7C7BAD",
        start_date:
          this.ks_fieldDetail[ks_gantt_fields.ks_task_start_date].type == "date"
            ? moment(each_task[ks_gantt_fields.ks_task_start_date]).toDate()
            : this.ksConversionUtcToLocal(
                moment(each_task[ks_gantt_fields.ks_task_start_date])
              ),
        end_date:
          this.ks_fieldDetail[ks_gantt_fields.ks_task_end_date].type == "date"
            ? moment(each_task[ks_gantt_fields.ks_task_end_date]).toDate()
            : this.ksConversionUtcToLocal(
                moment(each_task[ks_gantt_fields.ks_task_end_date])
              ),
        mark_as_important: each_task[ks_gantt_fields.ks_mark_as_important],
        deadline: gantt.config.ks_toggle_deadline
          ? each_task[ks_gantt_fields.ks_task_deadline]
          : false,
        ks_deadline_tooltip: each_task[ks_gantt_fields.ks_task_deadline]
          ? moment(each_task[ks_gantt_fields.ks_task_deadline]).toDate()
          : false,
        progress: each_task[ks_gantt_fields.ks_task_progress] / 100,
        ks_progress: each_task[ks_gantt_fields.ks_task_progress],
        ks_progress_enable: true,
        sequence: each_task[ks_gantt_fields.sequence],
        parent: each_task[ks_gantt_fields.ks_parent_task]
          ? each_task[ks_gantt_fields.ks_parent_task][0]
          : parent_group_id,
        //                'project_id': each_task.project_id,
        ks_allow_subtask: each_task[ks_gantt_fields.ks_allow_subtask],
        ks_schedule_mode: each_task[ks_gantt_fields.ks_schedule_mode],
        auto_scheduling:
          each_task[ks_gantt_fields.ks_schedule_mode] == "auto" ? true : false,
        constraint_type: each_task[ks_gantt_fields.ks_constraint_task_type]
          ? each_task[ks_gantt_fields.ks_constraint_task_type]
          : false,
        ks_constraint_type: each_task[ks_gantt_fields.ks_constraint_task_type]
          ? each_task[ks_gantt_fields.ks_constraint_task_type]
          : false,
        constraint_date: each_task[ks_gantt_fields.ks_constraint_task_date]
          ? this.ksConversionUtcToLocal(
              moment(each_task[ks_gantt_fields.ks_constraint_task_date])
            )
          : false,
        constraint_date_enable: each_task[
          ks_gantt_fields.ks_constraint_task_date
        ]
          ? true
          : false,
        stage_id: this.ks_get_stage_data(
          ks_gantt_fields.ks_task_stage_id,
          each_task[ks_gantt_fields.ks_task_stage_id]
        ),
        unscheduled: each_task[ks_gantt_fields.ks_unschedule],
        ks_owner_task: each_task[ks_gantt_fields.ks_owner_task],
        user: each_task[ks_gantt_fields.ks_owner_task]
          ? each_task[ks_gantt_fields.ks_owner_task][0]
          : 0,
        resource_working_hours:
          each_task[ks_gantt_fields.ks_resource_hours_per_day],
        ks_resource_hours_available: ks_resource_hours_available,
        type: ks_task_type,
        create_date: this.ksConversionUtcToLocal(moment(each_task.create_date)),
        project_id: each_task[ks_gantt_fields.project_id],
        partner_id: each_task[ks_gantt_fields.partner_id],
        company_id: each_task[ks_gantt_fields.company_id],
        ks_enable_task_duration:
          each_task[ks_gantt_fields.ks_enable_task_duration],
        ks_task_no_drag: this.ks_compute_task_drag(each_task),
        ks_task_duration: each_task[ks_gantt_fields.ks_task_duration],
        open: true,
      };

      // Manage multiple users.
      if (
        ks_gantt_fields &&
        ks_gantt_fields.ks_owner_task &&
        this.ks_fieldDetail[ks_gantt_fields.ks_owner_task].type == "many2many"
      )
        ks_gantt_data["user"] = each_task[ks_gantt_fields.ks_owner_task];

//       Check if parent task is available then set add parent otherwise set to false.

      if (each_task.parent_id && !this.state.KsAllTaskIds.includes(each_task.parent_id[0])){
        ks_gantt_data["parent"] = false
      }

      if (this.ks_export_field) {
        for (var index = 0; index <= this.ks_export_field.length; index++) {
          ks_gantt_data[this.ks_export_field[index]] =
            each_task[this.ks_export_field[index]];
        }
      }

      if (
        ks_gantt_data.start_date instanceof Date &&
        isFinite(ks_gantt_data.start_date) &&
        ks_gantt_data.end_date instanceof Date &&
        isFinite(ks_gantt_data.end_date)
      ) {
        ks_data.push(ks_gantt_data);
      } else {
        gantt.message({
          type: "warning",
          text: _t(
            ks_gantt_data.text +
              " not shown due to start/end date is not found."
          ),
        });
      }

      if (!gantt.config.ks_owner_task_list) {
        gantt.config.ks_owner_task_list = [
          { key: "0", label: "N/A", id: "0", text: "N/A" },
        ];
        gantt.config.ks_owner_task_dict = [];
      }
      if (
        each_task[ks_gantt_fields.ks_owner_task] &&
        each_task[ks_gantt_fields.ks_owner_task][0] &&
        gantt.config.ks_owner_task_dict.indexOf(
          each_task[ks_gantt_fields.ks_owner_task][0]
        ) < 0
      ) {
        gantt.config.ks_owner_task_dict.push(
          each_task[ks_gantt_fields.ks_owner_task][0]
        );
        if (each_task["ks_user_ids"]) {
          var ks_iterator = JSON.parse(
            each_task["ks_user_ids"].replace(/'/g, '"')
          );
          for (var i in ks_iterator) {
            gantt.config.ks_owner_task_list.push({
              key: ks_iterator[i][0],
              label: ks_iterator[i][1],
              id: ks_iterator[i][0],
              text: ks_iterator[i][1],
            });
          }
        } else {
          gantt.config.ks_owner_task_list.push({
            key: each_task[ks_gantt_fields.ks_owner_task][0],
            label: each_task[ks_gantt_fields.ks_owner_task][1],
            id: each_task[ks_gantt_fields.ks_owner_task][0],
            text: each_task[ks_gantt_fields.ks_owner_task][1],
          });
        }
      }
    },

    ks_compute_task_drag: function (each_task) {
      return false;
    },

    ks_get_stage_data: function (stage_field, stage_data) {
      if (stage_field && this.ks_fieldDetail[stage_field].type == "selection") {
        var ks_stage_str = undefined;
        this.ks_fieldDetail[stage_field].selection.forEach(function (
          selection_data
        ) {
          if (selection_data[0] == stage_data) {
            ks_stage_str = selection_data[1];
          }
        });
        return ks_stage_str;
      } else if (stage_data) {
        return stage_data;
      }
      return undefined;
    },

    ks_project_task_data_update: function (
      each_project_task,
      ks_links,
      ks_data,
      project_id
    ) {
      var ks_resource_hours_available = {};
      if (each_project_task.ks_resource_hours_available)
        ks_resource_hours_available = JSON.parse(
          each_project_task.ks_resource_hours_available
        );

      if (each_project_task.ks_task_link_json) {
        JSON.parse(each_project_task.ks_task_link_json).forEach(
          (item, index) => {
            ks_links.push({
              id: item.id,
              source: "task_" + item.source,
              target: "task_" + item.target,
              type: item.type,
            });
            // dict to check to duplicate link.
            gantt.config.ks_link_data.push({
              id: item.id,
              source: item.source,
              target: item.target,
              type: item.type,
            });
          }
        );
      }

      var ks_gantt_datas = {
        id: each_project_task.id,
        text: each_project_task.ks_task_name,
        color: each_project_task.ks_task_color
          ? each_project_task.ks_task_color
          : "#7C7BAD",
        start_date: this.ksConversionUtcToLocal(
          moment(each_project_task.ks_task_start_date)
        ),
        end_date: this.ksConversionUtcToLocal(
          moment(each_project_task.ks_task_end_date)
        ),
        parent: each_project_task.parent_id
          ? each_project_task.parent_id
          : project_id,
        mark_as_important: each_project_task.mark_as_important,
        deadline: gantt.config.ks_toggle_deadline
          ? each_project_task.deadline
          : false,
        ks_deadline_tooltip: each_project_task.deadline
          ? moment(each_project_task.deadline).toDate()
          : false,
        progress: each_project_task.progress / 100,
        ks_progress: each_project_task.progress,
        ks_progress_enable: false,
        sequence: each_project_task.sequence,
        ks_allow_subtask: each_project_task.ks_allow_subtask,
//                        'ks_allow_parent_task': each_project_task.ks_allow_subtask,
        ks_schedule_mode: each_project_task.ks_schedule_mode,
        auto_scheduling:
          each_project_task.ks_schedule_mode == "auto" ? true : false,
        constraint_type: each_project_task.constraint_type
          ? each_project_task.constraint_type
          : false,
        constraint_date: each_project_task.constraint_date
          ? this.ksConversionUtcToLocal(
              moment(each_project_task.constraint_date)
            )
          : false,
        constraint_date_enable: each_project_task.constraint_date
          ? true
          : false,
        stage_id: each_project_task.stage_id
          ? each_project_task.stage_id
          : undefined,
        unscheduled: each_project_task.unscheduled,
        resource_working_hours: each_project_task.resource_working_hours,
        ks_task_model: each_project_task.ks_task_model,
        ks_owner_task: each_project_task.ks_owner_task,
        user: each_project_task.ks_owner_task
          ? each_project_task.ks_owner_task[0]
          : 0,
        type: each_project_task.type,
        ks_resource_hours_available: ks_resource_hours_available,
        project_id: each_project_task.project_id,
        create_date: this.ksConversionUtcToLocal(
          moment(each_project_task.create_date)
        ),
        project_id: each_project_task.project_id,
        partner_id: each_project_task.partner_id,
        company_id: each_project_task.company_id,
        ks_enable_task_duration: each_project_task.ks_enable_task_duration,
        ks_task_duration: each_project_task.ks_task_duration,
        open: true,
      };
      // Manage multiple users.
      // if (
      //   each_project_task.ks_owner_task &&
      //   this.ks_fieldDetail[ks_owner_task].type == "many2many"
      // )
      //   ks_gantt_data["user"] = each_task[ks_gantt_fields.ks_owner_task];

      // Check if parent task is available then set add parent otherwise set to false.
      // if (!this.state.KsAllTaskIds.includes(ks_gantt_datas.parent))
      //   ks_gantt_datas["parent"] = false;

      if (this.ks_export_field) {
        for (var index = 0; index <= this.ks_export_field.length; index++) {
          ks_gantt_datas[this.ks_export_field[index]] =
            each_task[this.ks_export_field[index]];
        }
      }

      if (
        ks_gantt_datas.start_date instanceof Date &&
        isFinite(ks_gantt_datas.start_date) &&
        ks_gantt_datas.end_date instanceof Date &&
        isFinite(ks_gantt_datas.end_date)
      ) {
        ks_data.push(ks_gantt_datas);
      } else {
        gantt.message({
          type: "warning",
          text: _t(
            ks_gantt_data.text +
              " not shown due to start/end date is not found."
          ),
        });
      }

      if (!gantt.config.ks_owner_task_list) {
        gantt.config.ks_owner_task_list = [
          { key: "0", label: "N/A", id: "0", text: "N/A" },
        ];
        gantt.config.ks_owner_task_dict = [];
      }
      if (
        each_project_task.ks_owner_task &&
        each_project_task.ks_owner_task[0] &&
        gantt.config.ks_owner_task_dict.indexOf(
          each_project_task.ks_owner_task[0]
        ) < 0
      ) {
        gantt.config.ks_owner_task_dict.push(
          each_project_task.ks_owner_task[0]
        );
        gantt.config.ks_owner_task_list.push({
          key: each_project_task.ks_owner_task[0],
          label: each_project_task.ks_owner_task[1],
          id: each_project_task.ks_owner_task[0],
          text: each_project_task.ks_owner_task[1],
        });
      }
    },

    ks_task_quick_info: function () {
      // Hide quick info title.
      gantt.templates.quick_info_title = function (start, end, task) {
        return "";
      };
    },

    ks_linked_task_info: function () {
      var highlightTasks = [],
        highlightSearch = {};
      function reset(value) {
        if (value) {
          if (value.join() === highlightTasks.join()) {
            return;
          }
          highlightTasks = value;
          highlightSearch = {};
          highlightTasks.forEach(function (id) {
            highlightSearch[id] = true;
          });
          gantt.render();
        } else if (highlightTasks.length) {
          highlightTasks = [];
          highlightSearch = {};
          gantt.render();
        }
      }

      if (!gantt.config.ks_task_click_event) {
        let ks_task_click = gantt.attachEvent("onTaskClick", function (id) {
          var task = gantt.getTask(id);
          var group = gantt.getConnectedGroup(id);
          if (!group.tasks.length) {
            reset();
          } else {
            reset(group.tasks);
            gantt.message({
              text:
                "<strong>Selected task:</strong> " +
                task.text +
                "<br><strong>Connected Group:</strong><br> " +
                group.tasks
                  .map(function (t) {
                    return gantt.getTask(t).text;
                  })
                  .join("<br>"),
              expire: 5000,
            });
          }
          return true;
        });
        gantt.config.ks_task_click_event = ks_task_click;
      }

      gantt.templates.task_class = function (start, end, task) {
        if (highlightSearch[task.id]) return "ks_highlighted_task";
        return "";
      };

      gantt.config.ks_attached_events.push(
        gantt.attachEvent("onEmptyClick", function () {
          reset();
          return true;
        })
      );
    },

    // Manage side content of the task.
    ks_task_dynamic_content: function () {
      gantt.config.font_width_ratio = 7;
      var dateToStr = gantt.date.date_to_str("%j %F %H:%i");
      gantt.templates.leftside_text = function leftSideTextTemplate(
        start,
        end,
        task
      ) {
        var state = gantt.getState(),
          modes = gantt.config.drag_mode;
        if (state.drag_id == task.id) {
          if (
            state.drag_mode == modes.move ||
            (state.drag_mode == modes.resize && state.drag_from_start)
          ) {
            return dateToStr(gantt.roundDate(start));
          }
        }
        return "";
      };

      // Show overdue text.
      gantt.templates.rightside_text = function rightSideTextTemplate(
        start,
        end,
        task
      ) {
        var ks_task_text = "";
        if (task.deadline) {
          if (end.valueOf() > task.deadline.valueOf()) {
            var overdue = Math.ceil(
              Math.abs(
                (end.getTime() - task.deadline.getTime()) /
                  (24 * 60 * 60 * 1000)
              )
            );
            var text = " <b>Overdue: " + overdue + " days</b>";
            ks_task_text += text;
          }
        }

        function ksGetTaskFitValue(task) {
          var taskStartPos = gantt.posFromDate(task.start_date),
            taskEndPos = gantt.posFromDate(task.end_date);

          var width = taskEndPos - taskStartPos;
          var textWidth =
            ((task.text || "").length +
              (gantt.config.ks_task_dynamic_progress
                ? (" (" + Math.round(task.progress * 100) + "%)").length
                : 0)) *
            gantt.config.font_width_ratio;

          if (width < textWidth) {
            var ganttLastDate = gantt.getState().max_date;
            var ganttEndPos = gantt.posFromDate(ganttLastDate);
            if (ganttEndPos - taskEndPos < textWidth) {
              return "left";
            } else {
              return "right";
            }
          } else {
            return "center";
          }
        }

        // Show task end date while hover and drag task.
        var state = gantt.getState(),
          modes = gantt.config.drag_mode;

        if (state.drag_id == task.id) {
          if (
            state.drag_mode == modes.move ||
            (state.drag_mode == modes.resize && !state.drag_from_start)
          ) {
            if (
              state.drag_mode == modes.move ||
              (state.drag_mode == modes.resize && !state.drag_from_start)
            ) {
              if (ksGetTaskFitValue(task) === "right") {
                var ksTextWidth =
                  (task.text.length + 5) * gantt.config.font_width_ratio;
                return (
                  "<div style='margin-left:" +
                  ksTextWidth +
                  "px'>" +
                  dateToStr(gantt.roundDate(end)) +
                  "</div>"
                );
              }
              return dateToStr(gantt.roundDate(end));
            }
            //                        return dateToStr(gantt.roundDate(end));
          }
        }
        return ks_task_text;
      };

      gantt.templates.task_text = function taskTextTemplate(start, end, task) {
        var ks_task_text = "";
        if (
          getTaskFitValue(task) === "center" ||
          !gantt.ks_project_settings.ks_enable_task_dynamic_text
        ) {
          ks_task_text += task.text;
        }
        if (
          gantt.config.ks_task_dynamic_progress &&
          ks_task_text &&
          task.type != "project"
        ) {
          ks_task_text += " (" + Math.round(task.progress * 100) + "%)";
        }

        if (!ks_task_text.length) return "";
        return ks_task_text;
      };

      function getTaskFitValue(task) {
        var taskStartPos = gantt.posFromDate(task.start_date),
          taskEndPos = gantt.posFromDate(task.end_date);

        var width = taskEndPos - taskStartPos;
        var textWidth =
          ((task.text || "").length +
            (gantt.config.ks_task_dynamic_progress
              ? (" (" + Math.round(task.progress * 100) + "%)").length
              : 0)) *
          gantt.config.font_width_ratio;
        if (width < textWidth) {
          var ganttLastDate = gantt.getState().max_date;
          var ganttEndPos = gantt.posFromDate(ganttLastDate);
          if (ganttEndPos - taskEndPos < textWidth) {
            return "left";
          } else {
            return "right";
          }
        } else {
          return "center";
        }
      }
    },

    ks_days_off_func: function () {
      gantt.ignore_time = function (date) {
        if (
          this.config.ks_hide_date &&
          this.config.ks_days_off_selection &&
          this.config.ks_days_off_selection.indexOf(date.getDay()) > -1
        )
          return true;
        return false;
      };
    },

    ks_exclude_holiday_function: function () {
      // 24*7 availability
      gantt.setWorkTime({ day: 0, hours: ["0-24"] });
      gantt.setWorkTime({ day: 1, hours: ["0-24"] });
      gantt.setWorkTime({ day: 2, hours: ["0-24"] });
      gantt.setWorkTime({ day: 3, hours: ["0-24"] });
      gantt.setWorkTime({ day: 4, hours: ["0-24"] });
      gantt.setWorkTime({ day: 5, hours: ["0-24"] });
      gantt.setWorkTime({ day: 6, hours: ["0-24"] });

      // Exclude Days off day from work time;
      if (gantt.config.ks_days_off_selection) {
        for (var i = 0; i < gantt.config.ks_days_off_selection.length; i++) {
          gantt.setWorkTime({
            day: gantt.config.ks_days_off_selection[i],
            hours: false,
          });
        }
      }

      // function to set holiday
      for (var i = 0; i < gantt.config.ks_exclude_holiday.length; i++) {
        gantt.setWorkTime({
          date: this.ksConversionUtcToLocal(
            moment(gantt.config.ks_exclude_holiday[i])
          ),
          hours: false,
        });
      }

      gantt.config.work_time = true;
    },

    // Detached events from the gantt view.
    destroy: function () {
      gantt.clearAll();
      _.each(gantt.config.ks_attached_events, function (ks_event) {
        gantt.detachEvent(ks_event);
      });

      // close all active button on control panel.
      gantt.config.ks_no_of_days = false;
      gantt.config.ks_hide_grid_panel = false;
      gantt.config.ks_show_resource_panel = false;
      gantt.config.highlight_critical_path = false;
      gantt.config.ks_toggle_deadline = false;
      gantt.config.ks_enable_days_off = false;
      gantt.config.ks_hide_date = false;
      this._super.apply(this, arguments);
    },

    ks_select_columns: function () {
      gantt.config.ks_attached_events.push(
        gantt.attachEvent("onScaleClick", function (e, date) {
          this.config.ks_selected_column = date;
          var pos = gantt.getScrollState();
          gantt.render();
          gantt.scrollTo(pos.x, pos.y);
        })
      );
    },

    ks_gantt_layout: function () {
      // Function to manage gantt view layout.
      var ks_gantt_cols = [];
      gantt.config.ks_grid_width = ($(window).width() / 100) * 30;
      // If grid hide option is not enable then show the grid.
      if (!gantt.config.ks_hide_grid_panel) {
        ks_gantt_cols.push(
          {
            width: gantt.config.ks_grid_width,
            min_width: gantt.config.ks_grid_width,
            rows: [
              {
                view: "grid",
                scrollX: "gridScroll",
                scrollable: true,
                scrollY: "scrollVer",
              },
              { view: "scrollbar", id: "gridScroll", group: "horizontal" },
            ],
          },
          { resizer: true, width: 0 }
        );
      }
      // Add task timeline grid on the gantt chart.
      ks_gantt_cols.push(
        {
          rows: [
            { view: "timeline", scrollX: "scrollHor", scrollY: "scrollVer" },
            { view: "scrollbar", id: "scrollHor", group: "horizontal" },
          ],
        },
        { view: "scrollbar", id: "scrollVer" }
      );

      if (!gantt.config.rtl) {
        gantt.config.layout = {
          css: "gantt_container",
          rows: [{ cols: ks_gantt_cols }],
        };
      } else {
        gantt.config.layout = {
          css: "gantt_container",
          rows: [
            {
              cols: [
                {
                  rows: [
                    {
                      view: "timeline",
                      scrollX: "scrollHor",
                      scrollY: "scrollVer",
                    },
                    {
                      view: "scrollbar",
                      id: "scrollHor",
                      scroll: "x",
                      group: "hor",
                    },
                  ],
                },
              ],
            },
          ],
        };

        if (!gantt.config.ks_hide_grid_panel) {
          gantt.config.layout.rows[0].cols.push(
            { resizer: true, width: 1 },
            {
              width: gantt.config.ks_grid_width,
              min_width: gantt.config.ks_grid_width,
              rows: [
                {
                  view: "grid",
                  scrollable: true,
                  scrollX: "scrollHor1",
                  scrollY: "scrollVer",
                },
                {
                  view: "scrollbar",
                  id: "scrollHor1",
                  scroll: "x",
                  group: "hor",
                },
              ],
            }
          );
        }

        gantt.config.layout.rows[0].cols.push({
          view: "scrollbar",
          id: "scrollVer",
        });
      }

      // Check for resource panel also
      if (gantt.config.ks_show_resource_panel) this.ks_resource_panel();
    },

    // Task progress graph.
    ks_gantt_overlay_canvas: function () {
      function getChartScaleRange() {
        var tasksRange = gantt.getSubtaskDates();
        var cells = [];
        var scale = gantt.getScale();
        if (!tasksRange.start_date) {
          return scale.trace_x;
        }

        scale.trace_x.forEach(function (date) {
          if (date >= tasksRange.start_date && date <= tasksRange.end_date) {
            cells.push(date);
          }
        });
        return cells;
      }

      function getScalePaddings() {
        var scale = gantt.getScale();
        var dataRange = gantt.getSubtaskDates();

        var chartScale = getChartScaleRange();
        var newWidth = scale.col_width;
        var padding = {
          left: 0,
          right: 0,
        };

        if (dataRange.start_date) {
          var yScaleLabelsWidth = 48;
          // fine tune values in order to align chart with the scale range
          padding.left =
            gantt.posFromDate(dataRange.start_date) - yScaleLabelsWidth;
          padding.right =
            scale.full_width -
            gantt.posFromDate(dataRange.end_date) -
            yScaleLabelsWidth;
          padding.top = gantt.config.row_height - 12;
          padding.bottom = gantt.config.row_height - 12;
        }
        return padding;
      }

      function getProgressLine() {
        var tasks = gantt.getTaskByTime();
        var scale = gantt.getScale();
        var step = scale.unit;

        var timegrid = {};

        var totalDuration = 0;
        var today = new Date();
        gantt.eachTask(function (task) {
          if (gantt.isSummaryTask(task)) {
            return;
          }
          if (!task.duration) {
            return;
          }
          var currDate = gantt.date[scale.unit + "_start"](
            new Date(task.start_date)
          );
          while (currDate < task.end_date) {
            var date = currDate;
            currDate = gantt.date.add(currDate, 1, step);

            if (!gantt.isWorkTime({ date: date, task: task, unit: step })) {
              continue;
            }

            var timestamp = currDate.valueOf();
            if (!timegrid[timestamp]) {
              timegrid[timestamp] = {
                planned: 0,
                real: 0,
              };
            }

            timegrid[timestamp].planned += 1;
            if (date <= today) {
              timegrid[timestamp].real += 1 * (task.progress || 0);
            }

            totalDuration += 1;
          }
        });

        var cumulativePlannedDurations = [];
        var cumulativeRealDurations = [];
        var cumulativePredictedDurations = [];
        var totalPlanned = 0;
        var totalReal = 0;

        var chartScale = getChartScaleRange();
        var dailyRealProgress = -1;
        var totalPredictedProgress = 0;
        for (var i = 0; i < chartScale.length; i++) {
          var start = new Date(chartScale[i]);
          var end = gantt.date.add(start, 1, step);
          var cell = timegrid[start.valueOf()] || { planned: 0, real: 0 };
          totalPlanned = cell.planned + totalPlanned;

          cumulativePlannedDurations.push(totalPlanned);
          if (start <= today) {
            totalReal = (cell.real || 0) + totalReal;
            cumulativeRealDurations.push(totalReal);
            cumulativePredictedDurations.push(null);
          } else {
            if (dailyRealProgress < 0) {
              dailyRealProgress = totalReal / cumulativeRealDurations.length;
              totalPredictedProgress = totalReal;
              cumulativePredictedDurations.pop();
              cumulativePredictedDurations.push(totalPredictedProgress);
            }
            totalPredictedProgress += dailyRealProgress;
            cumulativePredictedDurations.push(totalPredictedProgress);
          }
        }

        for (var i = 0; i < cumulativePlannedDurations.length; i++) {
          cumulativePlannedDurations[i] = Math.round(
            (cumulativePlannedDurations[i] / totalPlanned) * 100
          );
          if (cumulativeRealDurations[i] !== undefined) {
            cumulativeRealDurations[i] = Math.round(
              (cumulativeRealDurations[i] / totalPlanned) * 100
            );
          }

          if (cumulativePredictedDurations[i] !== null) {
            cumulativePredictedDurations[i] = Math.round(
              (cumulativePredictedDurations[i] / totalPlanned) * 100
            );
          }
        }
        return {
          planned: cumulativePlannedDurations,
          real: cumulativeRealDurations,
          predicted: cumulativePredictedDurations,
        };
      }

      var myChart;
      var dateToStr = gantt.date.date_to_str("%F %j, %Y");
      var overlayControl = gantt.ext.overlay;
      var lineOverlay = overlayControl.addOverlay(
        function (container) {
          var scaleLabels = [];
          var chartScale = getChartScaleRange();
          chartScale.forEach(function (date) {
            scaleLabels.push(dateToStr(date));
          });
          var values = getProgressLine();

          // Condition to handle high data that prevent graph to render.
          if (values.planned.length > 1000) {
            this.displayNotification({
              message: _t(
                "We are not able to show graph for large duration, please change the view scale"
              ),
              type: "danger",
            });
            gantt.config.ks_overlay_result = false;
            return false;
          }

          var canvas = document.createElement("canvas");
          container.appendChild(canvas);
          canvas.style.height = container.offsetHeight + "px";
          canvas.style.width = container.offsetWidth + "px";

          var ctx = canvas.getContext("2d");
          if (myChart) {
            myChart.destroy();
          }
          myChart = new Chart(ctx, {
            type: "line",
            data: {
              datasets: [
                {
                  label: "Planned progress",
                  backgroundColor: "#001eff",
                  borderColor: "#001eff",
                  data: values.planned,
                  fill: false,
                  cubicInterpolationMode: "monotone",
                },
                {
                  label: "Real progress",
                  backgroundColor: "#ff5454",
                  borderColor: "#ff5454",
                  data: values.real,
                  fill: false,
                  cubicInterpolationMode: "monotone",
                },
                {
                  label: "Real progress (predicted)",
                  backgroundColor: "#ff5454",
                  borderColor: "#ff5454",
                  data: values.predicted,
                  borderDash: [5, 10],
                  fill: false,
                  cubicInterpolationMode: "monotone",
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              layout: {
                padding: getScalePaddings(),
              },
              onResize: function (chart, newSize) {
                var dataRange = gantt.getSubtaskDates();
                if (dataRange.start_date) {
                  // align chart with the scale range
                  chart.options.layout.padding = getScalePaddings();
                }
              },
              legend: {
                display: false,
              },
              tooltips: {
                mode: "index",
                intersect: false,
                callbacks: {
                  label: function (tooltipItem, data) {
                    var dataset = data.datasets[tooltipItem.datasetIndex];
                    return (
                      dataset.label +
                      ": " +
                      dataset.data[tooltipItem.index] +
                      "%"
                    );
                  },
                },
              },
              hover: {
                mode: "nearest",
                intersect: true,
              },
              scales: {
                xAxes: [
                  {
                    labels: scaleLabels,
                    gridLines: {
                      display: false,
                    },
                    ticks: {
                      display: false,
                    },
                  },
                  {
                    position: "top",
                    labels: scaleLabels,
                    gridLines: {
                      display: false,
                    },
                    ticks: {
                      display: false,
                    },
                  },
                ],
                yAxes: [
                  {
                    display: true,
                    gridLines: {
                      display: false,
                    },
                    ticks: {
                      display: true,
                      min: 0,
                      max: 100,
                      stepSize: 10,
                      callback: function (current) {
                        if (current > 100) {
                          return "";
                        }
                        return current + "%";
                      },
                    },
                  },
                  {
                    display: true,
                    position: "right",
                    gridLines: {
                      display: false,
                    },
                    ticks: {
                      display: true,
                      min: 0,
                      max: 100,
                      stepSize: 10,
                      callback: function (current) {
                        if (current > 100) {
                          return "";
                        }
                        return current + "%";
                      },
                    },
                  },
                ],
              },
            },
          });
          return canvas;
        }.bind(this)
      );

      gantt.config.ks_overlay_result = true;
      gantt.config.lineOverlay = lineOverlay;
    },

    // Gantt view resource panel.
    ks_resource_panel: function () {
      /*
       *   Function to create gantt datastore for resource.
       */
      gantt.config.ks_resource_panel_render = true;
      var resourcePanelConfig = {
        columns: [
          {
            name: "name",
            label: "Name",
            template: function (resource) {
              return resource.label;
            },
          },
        ],
      };

      function calculateResourceLoad(tasks, scale) {
        var step = scale.unit;
        var timegrid = {};
        var scale_range = [];
        var ks_scale_range = scale.min_date;
        for (var i = 0; i < tasks.length; i++) {
          var task = tasks[i];
          var currDate = gantt.date[step + "_start"](new Date(task.start_date));
          while (currDate < task.end_date) {
            var date = currDate;
            var ks_scale_start_date = date; // Scale start date.
            currDate = gantt.date.add(currDate, scale.step, step); // Scale end date.
            var timestamp = date.valueOf();
            var ks_curr_date = date;
            // Check if current date is not the scale initial value.
            if (
              step == "hour" &&
              (scale.step == 2 || scale.step == 4 || scale.step == 8)
            ) {
              while (ks_curr_date.getHours() % scale.step) {
                var setHours = ks_curr_date.getHours() - 1;
                ks_curr_date.setHours(setHours);
                ks_curr_date.setSeconds(0);
                ks_curr_date.setMinutes(0);
                timestamp = ks_curr_date.valueOf();
                ks_scale_start_date = ks_curr_date;
              }
            }

            if (!timegrid[timestamp]) timegrid[timestamp] = 0;

            // If resource mode set to task
            if (gantt.config.ks_resource_mode == "tasks") {
              timegrid[timestamp] += 1;
            }
            // Resource mode set to hours.
            // Task Start -> task.start_date;
            // Task End -> task.end_date
            // Scale Start -> ks_scale_start_date
            // Scale End -> currDate
            // Compute hours on the basis of employee working hours.
            else var ks_start_hours;
            var ks_end_hours;
            // Compute start hour
            if (task.start_date.valueOf() == ks_scale_start_date.valueOf())
              ks_start_hours = new Date(ks_scale_start_date);
            if (
              task.start_date > ks_scale_start_date &&
              task.start_date < currDate
            )
              ks_start_hours = new Date(task.start_date);
            if (
              task.start_date < ks_scale_start_date &&
              task.end_date > ks_scale_start_date
            )
              ks_start_hours = new Date(ks_scale_start_date);

            // Compute end hour
            if (task.end_date.valueOf() == currDate.valueOf())
              ks_end_hours = new Date(currDate);
            if (task.end_date > ks_scale_start_date && task.end_date < currDate)
              ks_end_hours = new Date(task.end_date);
            if (task.end_date > currDate && task.start_date < currDate)
              ks_end_hours = new Date(currDate);

            while (ks_start_hours < ks_end_hours) {
              if (Object.keys(task.ks_resource_hours_available).length) {
                // Working hour key.
                var ks_key = ks_start_hours.getDay();
                if (ks_key < 0) ks_key = 6;

                var ks_avail_hours = task.ks_resource_hours_available[ks_key];
                if (
                  ks_avail_hours &&
                  ks_avail_hours.indexOf(ks_start_hours.getHours()) > -1
                ) {
                  timegrid[timestamp] += 1;
                }
              }
              ks_start_hours.setHours(ks_start_hours.getHours() + 1);
            }
          }
        }

        var timetable = [];
        var start, end;
        // Monkey patching for resource mode tasks
        if (gantt.config.ks_resource_mode == "tasks") {
          for (var i in timegrid) {
            start = new Date(i * 1);
            end = gantt.date.add(start, scale.step, step);
            var ks_count_task = 0;
            for (var ks_index = 0; ks_index < tasks.length; ks_index++) {
              if (start.getTime() == tasks[ks_index].start_date.getTime()) {
                ks_count_task += 1;
              } else if (
                start.getTime() < tasks[ks_index].start_date.getTime() &&
                tasks[ks_index].start_date.getTime() < end.getTime()
              ) {
                ks_count_task += 1;
              } else if (
                tasks[ks_index].start_date.getTime() < start.getTime() &&
                end.getTime() <= tasks[ks_index].end_date.getTime()
              ) {
                ks_count_task += 1;
              } else if (
                tasks[ks_index].start_date.getTime() < start.getTime() &&
                tasks[ks_index].end_date.getTime() <= end.getTime() &&
                tasks[ks_index].start_date.getTime() != end.getTime() &&
                start < tasks[ks_index].end_date.getTime()
              ) {
                ks_count_task += 1;
              }
            }

            timetable.push({
              start_date: start,
              end_date: end,
              value: ks_count_task,
            });
          }

          return timetable;
        }

        for (var i in timegrid) {
          start = new Date(i * 1);
          end = gantt.date.add(start, scale.step, step);
          timetable.push({
            start_date: start,
            end_date: end,
            value: timegrid[i],
          });
        }

        return timetable;
      }

      var renderResourceLine = function (resource, timeline) {
        var tasks = gantt.getTaskBy("user", resource.id);
        var timetable = calculateResourceLoad(tasks, timeline.getScale());
        var row = document.createElement("div");

        for (var i = 0; i < timetable.length; i++) {
          var day = timetable[i];

          var css = "";
          if (day.value <= 8) {
            css = "gantt_resource_marker gantt_resource_marker_ok";
          } else {
            css = "gantt_resource_marker gantt_resource_marker_overtime";
          }

          var sizes = timeline.getItemPosition(
            resource,
            day.start_date,
            day.end_date
          );
          var el = document.createElement("div");
          el.className = css;

          el.style.cssText = [
            "left:" + sizes.left + "px",
            "width:" + sizes.width + "px",
            "position:absolute",
            "height:" + (gantt.config.row_height - 1) + "px",
            "line-height:" + sizes.height + "px",
            "top:" + sizes.top + "px",
          ].join(";");

          el.innerHTML = day.value;
          row.appendChild(el);
        }
        return row;
      };

      var resourceLayers = [renderResourceLine, "taskBg"];

      var ks_resource_mode_hours = document.createElement("input");
      ks_resource_mode_hours.setAttribute("type", "radio");
      ks_resource_mode_hours.className = "ks-resource-mode";
      ks_resource_mode_hours.setAttribute("name", "resource-mode");
      ks_resource_mode_hours.setAttribute("value", "hours");

      var ks_resource_mode_tasks = document.createElement("input");
      ks_resource_mode_tasks.setAttribute("type", "radio");
      ks_resource_mode_tasks.className = "ks-resource-mode";
      ks_resource_mode_tasks.setAttribute("name", "resource-mode");
      ks_resource_mode_tasks.setAttribute("value", "tasks");

      if (gantt.config.ks_resource_mode == "tasks") {
        ks_resource_mode_tasks.setAttribute("checked", "true");
      } else if (gantt.config.ks_resource_mode == "histogram") {
        ks_resource_mode_histogram.setAttribute("checked", "true");
      } else {
        ks_resource_mode_hours.setAttribute("checked", "true");
      }

      if (!gantt.config.rtl) {
        gantt.config.layout.rows.push(
          { resizer: true, width: 1, next: "resources" },
          {
            height: 35,
            cols: [
              {
                html: "",
                group: "grids",
                width: gantt.config.ks_grid_width,
                min_width: gantt.config.ks_grid_width,
              },
              { resizer: true, width: 1 },
              {
                html:
                  "<label> Hours " +
                  ks_resource_mode_hours.outerHTML +
                  "</label> <label> Tasks " +
                  ks_resource_mode_tasks.outerHTML +
                  "</label>",
                css: "resource-controls",
              },
            ],
          },
          {
            id: "resources",
            config: resourcePanelConfig,
            cols: [
              {
                view: "grid",
                id: "resourceGrid",
                group: "grids",
                bind: "resources",
                scrollY: "resourceVScroll",
                width: gantt.config.ks_grid_width,
                min_width: gantt.config.ks_grid_width,
              },
            ],
          }
        );
        // Insert div for task resource type hours/tasks
        if (
          gantt.config.ks_resource_mode == "tasks" ||
          gantt.config.ks_resource_mode == "hours" ||
          gantt.config.ks_resource_mode === undefined
        ) {
          gantt.config.layout.rows[3].cols.push(
            { resizer: true, width: 1, group: "vertical" },
            {
              view: "timeline",
              id: "resourceTimeline",
              bind: "resources",
              bindLinks: null,
              layers: resourceLayers,
              scrollX: "scrollHor",
              scrollY: "resourceVScroll",
            },
            { view: "scrollbar", id: "resourceVScroll", group: "vertical" }
          );
        }
      } else {
        gantt.config.layout.rows.push(
          { resizer: true, width: 1, next: "resources" },
          {
            height: 35,
            cols: [
              {
                html: "",
                group: "grids",
                width: gantt.config.ks_grid_width,
                min_width: gantt.config.ks_grid_width,
              },
              { resizer: true, width: 1 },
              {
                html:
                  "<label>Hours" +
                  ks_resource_mode_hours.outerHTML +
                  "</label> <label>Tasks" +
                  ks_resource_mode_tasks.outerHTML +
                  "</label>",
                css: "resource-controls",
              },
            ],
          },
          {
            id: "resources",
            config: resourcePanelConfig,
            cols: [
              {
                view: "timeline",
                id: "resourceTimeline",
                bind: "resources",
                bindLinks: null,
                layers: resourceLayers,
                scrollX: "scrollHor",
                scrollY: "resourceVScroll",
              },
              { resizer: true, width: 1, group: "vertical" },
              {
                view: "grid",
                id: "resourceGrid",
                group: "grids",
                bind: "resources",
                scrollY: "resourceVScroll",
                width: gantt.config.ks_grid_width + 15,
                min_width: gantt.config.ks_grid_width,
              },
              { view: "scrollbar", id: "resourceVScroll", group: "vertical" },
            ],
          }
        );
      }

      gantt.config.ks_resources_store = gantt.createDatastore({
        name: "resources",
        initItem: function (item) {
          item.id = item.key || gantt.uid();
          return item;
        },
      });
      var tasksStore = gantt.getDatastore("task");
      tasksStore.attachEvent("onStoreUpdated", function (id, item, mode) {
        gantt.config.ks_resources_store.refresh();
      });
    },

    ks_gantt_plugins: function () {
      // Activate gantt view plugins.
      gantt.plugins({
        marker: true,
        keyboard_navigation: true,
        tooltip: true,
        critical_path: true,
        drag_timeline: true,
        auto_scheduling: true,
        quick_info:
          this.ks_model_name == "project.project" ||
          this.ks_enable_quickinfo_extension
            ? true
            : false,
        fullscreen: true,
        overlay: true,
      });
    },

    // Set left grid columns.
    ks_left_grid_columns: function () {
      var ks_col_header = QWeb.render("ks_gantt_view_base.ks_col_header"),
        ks_col_content_buttons = function (task) {
          return QWeb.render("ks_gantt_view_base.ks_col_content_buttons", {
            task: task,
            create:
              this.ks_gantt_config &&
              this.ks_gantt_config.ks_hide_sub_task_icon == "True"
                ? false
                : this.ks_isCreate,
          });
        }.bind(this);
      // Column defined here.
      let ks_gantt_config_columns = [
        {
          name: "ks_progress_color",
          label: "",
          width: 7,
          template: function (ks_task) {
            if (["task", "milestone"].indexOf(ks_task.type) > -1) {
              if (ks_task.ks_progress == 0) {
                // Red
                return "<div class='ks_progress_sec ks_progress_red'></div>";
              } else if (ks_task.ks_progress > 0 && ks_task.ks_progress < 100) {
                // Yellow
                return "<div class='ks_progress_sec ks_progress_yellow'></div>";
              } else if (ks_task.ks_progress == 100) {
                // green.
                return "<div class='ks_progress_sec ks_progress_green'></div>";
              }
            }
            return "";
          },
        },
        {
          name: "text",
          label: _("Title"),
          tree: true,
          width: 200,
          resize: true,
          template: function (obj) {
            var ks_column_str = "";
            if (obj.deadline) {
              var deadline = new Date(obj.deadline);
              if (deadline && obj.end_date > deadline) {
                ks_column_str += '<div class="overdue-indicator">!</div>';
              }
            }
            if (obj.mark_as_important == "1") {
              ks_column_str +=
                "<div class='ks-gv-mark-as-important'><i class='fa fa-star'></i></div>";
            }
            return ks_column_str + obj.text;
          },
        },
        {
          name: "duration",
          label: _("Duration"),
          align: "center",
          resize: true,
          width: 95,
          template: function (task) {
            if (task.unscheduled) {
              return "";
            }
            //                        if(task.ks_task_duration){
            //                            return task.ks_task_duration + ' days';
            //                        }
            let ks_task_difference = "";
            let ks_diff_ms = task.end_date - task.start_date;
            let ks_hours = Math.floor(ks_diff_ms / 1000 / 60 / 60);

            let ks_days = Math.floor(ks_hours / 24);
            let ks_rem_hours = ks_hours % 24;
            let ks_minute = Math.floor(ks_diff_ms / 60000) % 60;
            let ks_seconds = (ks_diff_ms / 1000) % 60;

            if (ks_days) ks_task_difference += ks_days + _t(" day, ");

            ks_task_difference +=
              (ks_rem_hours < 10 ? "0" + ks_rem_hours : ks_rem_hours) + ":";
            ks_task_difference += ks_minute < 10 ? "0" + ks_minute : ks_minute;
            task.ks_task_difference = ks_task_difference;
            task.ks_task_duration = ks_task_difference;
            return ks_task_difference;
          },
        },
        {
          name: "start_date",
          align: "center",
          label: _("Start Time"),
          resize: true,
          width: 120,
          template: function (task) {
            if (task.start_date) {
              return gantt.ks_gantt_view_datetime_format(task.start_date);
            }
            return "";
          },
        },
      ];
      // Check for owner columns.
      if (this.ks_gantt_config && !this.ks_gantt_config.ks_hide_grid_owner) {
        ks_gantt_config_columns.push({
          name: "owner",
          width: 80,
          label: _("Owner"),
          align: "center",
          sort: false,
          template: function (task) {
            if (task.ks_owner_task) {
              if (_.isArray(task.ks_owner_task)) return task.ks_owner_task[1];
              else return task.ks_owner_task;
            }
            return "";
          },
        });
      }
      // Added grid button.
      ks_gantt_config_columns.push({
        name: "buttons",
        label: this.ks_isCreate ? ks_col_header : false,
        width: 75,
        sort: false,
        template: ks_col_content_buttons,
      });

      gantt.config.columns = ks_gantt_config_columns;
    },

    // Return zoom configuration.
    // gantt.config.scales
    ks_zoom_config: function () {
      // Gantt view scaling configuration.
      return {
        levels: [
          {
            name: "15 minutes",
            scale_height: 50,
            min_column_width: 40,
            scales: [
              {
                unit: "hour",
                step: 1,
                format: "%d %M - %h %A",
              },
              {
                unit: "minute",
                step: 15,
                format: "%i",
              },
            ],
          },
          {
            name: "30 minutes",
            scale_height: 50,
            min_column_width: 60,
            scales: [
              {
                unit: "hour",
                step: 1,
                format: "%d %M - %h %A",
              },
              {
                unit: "minute",
                step: 30,
                format: "%i",
              },
            ],
          },
          {
            name: "2 hour",
            scale_height: 50,
            min_column_width: 40,
            scales: [
              {
                unit: "day",
                step: 1,
                format: "%d %M",
              },
              {
                unit: "hour",
                step: 2,
                format: "%h %A",
              },
            ],
          },
          {
            name: "4 hour",
            scale_height: 50,
            min_column_width: 40,
            scales: [
              {
                unit: "day",
                step: 1,
                format: "%d %M",
              },
              {
                unit: "hour",
                step: 4,
                format: "%h %A",
              },
            ],
          },
          {
            name: "8 hour",
            scale_height: 50,
            min_column_width: 40,
            scales: [
              {
                unit: "day",
                step: 1,
                format: "%d %M",
              },
              {
                unit: "hour",
                step: 8,
                format: "%h %A",
              },
            ],
          },
          {
            name: "day",
            scale_height: 50,
            min_column_width: 40,
            scales: [
              {
                unit: "day",
                step: 1,
                format: "%d %M",
              },
              {
                unit: "hour",
                step: 1,
                format: "%h %A",
              },
            ],
          },
          {
            name: "week",
            scale_height: 50,
            min_column_width: 40,
            scales: [
              {
                unit: "week",
                step: 1,
                format: function (date) {
                  var dateToStr = gantt.date.date_to_str("%d %M");
                  var endDate = gantt.date.add(date, +6, "day");
                  return dateToStr(date) + " - " + dateToStr(endDate);
                },
              },
              {
                unit: "day",
                step: 1,
                format: "%j %D",
              },
            ],
          },
          {
            name: "month",
            scale_height: 50,
            min_column_width: 50,
            scales: [
              {
                unit: "month",
                format: "%F, %Y",
              },
              {
                unit: "day",
                step: 1,
                format: "%j %D",
              },
            ],
          },
          {
            name: "quarter",
            scale_height: 50,
            min_column_width: 60,
            scales: [
              {
                unit: "year",
                step: 1,
                format: "%Y",
              },
              {
                unit: "month",
                step: 3,
                format: "%F",
              },
            ],
          },
          {
            name: "year",
            scale_height: 50,
            min_column_width: 60,
            scales: [
              {
                unit: "year",
                step: 1,
                format: "%Y",
              },
              {
                unit: "month",
                step: 1,
                format: "%F",
              },
            ],
          },
        ],
        useKey: "altKey",
        trigger: "wheel",
        element: function () {
          return gantt.$root.querySelector(".gantt_task");
        },
      };
    },

    // Set scale/zoom drop-down value with gantt view current scale.
    ks_set_scale_dropdown: function () {
      gantt.attachEvent("onGanttRender", function () {
        var ks_selected_zoom_level =
          gantt.ext.zoom.getLevels()[gantt.ext.zoom.getCurrentLevel()];
        var $ks_zoom_selection = $("select#ks_gantt_view_zoom");
        if (
          $ks_zoom_selection.length &&
          ks_selected_zoom_level.name != $ks_zoom_selection[0].value
        ) {
          $ks_zoom_selection[0].value = ks_selected_zoom_level.name;
        }
      });
    },

    ks_full_screen_element: function () {
      gantt.ext.fullscreen.getFullscreenElement = function () {
        return document.getElementById("ks_main_gantt_container");
      };

      // Manage gantt view height before gantt expand.
      gantt.attachEvent(
        "onBeforeExpand",
        function () {
          this.$(".ks_gantt_view_content").height(window.outerHeight);
          return true;
        }.bind(this)
      );

      gantt.attachEvent(
        "onBeforeCollapse",
        function () {
          var ks_extra_space =
            $(".o_main_navbar").height() +
            $(".o_control_panel").height() +
            $(".ks_gantt_right_control").height();
          this.$(".ks_gantt_view_content").height(
            window.outerHeight - ks_extra_space
          );
          return true;
        }.bind(this)
      );
    },

    ks_handle_critical_tasks: function () {
      // Gantt view show critical task.
      gantt.templates.task_class = function (start, end, task) {
        if (gantt.config.highlight_critical_path && gantt.isCriticalTask(task))
          return "critical_task";
        return "";
      };

      // Gantt view show critical task link.
      gantt.templates.link_class = function (link) {
        if (gantt.config.highlight_critical_path && gantt.isCriticalLink(link))
          return "critical_link";
        return "";
      };
    },

    ks_handle_selected_columns: function () {
      // Highlight selected column on the gantt view.
      function ks_is_selected_column(column_date) {
        if (
          gantt.config.ks_selected_column &&
          column_date.valueOf() == gantt.config.ks_selected_column.valueOf()
        ) {
          return true;
        }
        return false;
      }
    },

    ks_handle_non_working_timeline: function () {
      // Highlight selected column on the gantt view.
      function ks_is_selected_column(column_date) {
        if (
          gantt.config.ks_selected_column &&
          column_date.valueOf() == gantt.config.ks_selected_column.valueOf()
        ) {
          return true;
        }
        return false;
      }

      // Function to change timeline color for non-working days.
      gantt.templates.timeline_cell_class = function (item, date) {
        // highlight selected column.
        if (ks_is_selected_column(date)) return "highlighted-column";
        // highlight days off days on the gantt view.
        // if resource doesn't have the available day.
        if (
          item.ks_owner_task &&
          item.ks_resource_hours_available &&
          !item.ks_resource_hours_available[date.getDay()] &&
          gantt.config.ks_enable_days_off
        ) {
          return "weekend";
        }
        if (
          item.ks_owner_task &&
          item.ks_resource_hours_available &&
          item.ks_resource_hours_available[date.getDay()] &&
          gantt.config.ks_enable_days_off
        ) {
          if (
            item.ks_resource_hours_available[date.getDay()].indexOf(
              date.getHours()
            ) < 0 &&
            gantt.getScale().unit == "hour"
          ) {
            return "weekend";
          }
        }
        if (!gantt.isWorkTime(date) && gantt.config.ks_enable_days_off) {
          return "weekend";
        }
      };
    },

    ks_handle_group_by_text: function () {
      // Text color bold when data is grouped.
      gantt.templates.grid_row_class = function (start, end, task) {
        if (task.ks_group_lvl) {
          return "ks_text_bold";
        }
        return "";
      };
    },

    ks_handle_gantt_view_marker: function () {
      // Today Marker
      gantt.addMarker({
        start_date: new Date(),
        css: "today",
        text: "Today",
        title: gantt.ks_gantt_view_datetime_format(new Date()),
      });
      if (this.ks_project_start) {
        // Project Start Marker.
        gantt.addMarker({
          start_date: this.ksConversionUtcToLocal(
            moment(this.ks_project_start)
          ),
          css: "status_line",
          text: _("Start"),
          title: gantt.ks_gantt_view_datetime_format(
            this.ksConversionUtcToLocal(moment(this.ks_project_start))
          ),
        });
      }
      if (this.ks_project_end) {
        // Project End Marker.
        gantt.addMarker({
          start_date: this.ksConversionUtcToLocal(moment(this.ks_project_end)),
          css: "status_line",
          text: _("End"),
          title: gantt.ks_gantt_view_datetime_format(
            this.ksConversionUtcToLocal(moment(this.ks_project_end))
          ),
        });
      }
    },

    ks_handle_task_side_content: function () {
      function ksRenderDiv(task, date, className) {
        var el = document.createElement("div");
        el.className = className;
        var sizes = gantt.getTaskPosition(task, date);
        el.style.left = sizes.left + "px";
        el.style.top = sizes.top + "px";
        return el;
      }

      function ksGetTaskFitValue(task) {
        var taskStartPos = gantt.posFromDate(task.start_date),
          taskEndPos = gantt.posFromDate(task.end_date);

        var width = taskEndPos - taskStartPos;
        var textWidth =
          ((task.text || "").length +
            (gantt.config.ks_task_dynamic_progress
              ? (" (" + Math.round(task.progress * 100) + "%)").length
              : 0)) *
          gantt.config.font_width_ratio;

        if (width < textWidth) {
          var ganttLastDate = gantt.getState().max_date;
          var ganttEndPos = gantt.posFromDate(ganttLastDate);
          if (ganttEndPos - taskEndPos < textWidth) {
            return "left";
          } else {
            return "right";
          }
        } else {
          return "center";
        }
      }

      function ks_compute_task_duration(task) {
        if (task.unscheduled) {
          return "";
        }
        let ks_task_difference = "";
        let ks_diff_ms = task.end_date - task.start_date;
        let ks_hours = Math.floor(ks_diff_ms / 1000 / 60 / 60);

        let ks_days = Math.floor(ks_hours / 24);
        ks_task_difference += ks_days + " days";
        return ks_task_difference;
      }

      // Draw deadline function manages the side content of the task eg. deadline icon, task name, etc.
      gantt.config.ks_task_extra_info = function draw_deadline(task) {
        var ks_left_text_position = 60;
        var ks_right_text_position = 10;
        var constraintType = gantt.getConstraintType(task);
        var types = gantt.config.constraint_types;
        var els = document.createElement("div");
        var ks_earliestStart_exist = false;

        if (task.unscheduled) {
          return false;
        }

        if (
          constraintType != types.ASAP &&
          constraintType != types.ALAP &&
          task.constraint_date &&
          task.constraint_date_enable
        ) {
          var dates = gantt.getConstraintLimitations(task);
          if (dates.earliestStart) {
            ks_earliestStart_exist = true;
            ks_left_text_position += 40;
            els.appendChild(
              ksRenderDiv(
                task,
                dates.earliestStart,
                "constraint-marker earliest-start"
              )
            );
          }

          if (dates.latestEnd) {
            ks_right_text_position += 40;
            els.appendChild(
              ksRenderDiv(task, dates.latestEnd, "constraint-marker latest-end")
            );
          }

          els.title =
            gantt.locale.labels[constraintType] +
            " " +
            gantt.templates.task_date(task.constraint_date);
        }

        if (task.progress >= 1) {
          ks_left_text_position += 30;
          var el = document.createElement("div");
          el.className = "ks_task_done";
          el.title = "Task completed";
          var sizes = gantt.getTaskPosition(task, task.start_date);
          el.style.left =
            sizes.left - 50 - (ks_earliestStart_exist ? 30 : 0) + "px";
          el.style.top = sizes.top + "px";
          els.appendChild(el);
        }

        // No of days in gantt chart.
        if (gantt.config.ks_no_of_days) {
          var task_duration_el = document.createElement("div");
          task_duration_el.textContent = ks_compute_task_duration(task);
          task_duration_el.className = "ks_task_left_text";
          var sizes = gantt.getTaskPosition(task, task.start_date);
          task_duration_el.style.left =
            sizes.left - ks_left_text_position + "px";
          task_duration_el.style.top = sizes.top + "px";
          els.appendChild(task_duration_el);
          ks_left_text_position += 30;
        }

        if (
          ksGetTaskFitValue(task) === "left" &&
          gantt.ks_project_settings.ks_enable_task_dynamic_text
        ) {
          var el = document.createElement("div");
          el.textContent = task.text;
          if (gantt.config.ks_task_dynamic_progress) {
            el.textContent += " (" + Math.round(task.progress * 100) + "%)";
          }
          el.className = "ks_task_left_text";
          var sizes = gantt.getTaskPosition(task, task.start_date);
          var canvas = document.createElement("canvas");
          var ctx = canvas.getContext("2d");
          ks_left_text_position += ctx.measureText(el.textContent).width;
          el.style.left = sizes.left - (ks_left_text_position + 35) + "px";
          el.style.top = sizes.top + "px";
          els.appendChild(el);
        }

        var ks_task_text = "";
        // Manage right side task dynamic text.
        if (ksGetTaskFitValue(task) === "right") {
          // check if dynamic text is enabled then move the task text.
          if (gantt.ks_project_settings.ks_enable_task_dynamic_text) {
            var el = document.createElement("div");
            el.textContent = task.text;
            if (gantt.config.ks_task_dynamic_progress) {
              el.textContent += " (" + Math.round(task.progress * 100) + "%)";
            }
            el.className = "ks_task_left_text";
            var sizes = gantt.getTaskPosition(task, task.start_date);
            el.style.left =
              sizes.left +
              sizes.width +
              ks_right_text_position +
              (task.deadline &&
              task.deadline.valueOf() &&
              task.end_date.valueOf() > task.deadline.valueOf()
                ? 110
                : 0) +
              (task.type == "milestone" ? 20 : 0) +
              "px";
            el.style.top = sizes.top + "px";
            els.appendChild(el);
          }
        }

        // Add deadline icon on timeline.
        if (task.deadline) {
          var el = document.createElement("div");
          el.className = "ks_deadline";
          var sizes = gantt.getTaskPosition(task, task.deadline);

          el.style.left = sizes.left + "px";
          el.style.top = sizes.top + "px";

          el.setAttribute("title", gantt.templates.task_date(task.deadline));
          els.appendChild(el);
        }

        if (els.children.length) return els;
        return false;
      };
    },

    ks_control_panel_slider: function () {
      var ksScrollDuration = 300;

      // left-right buttons
      var ksLeftPaddle = document.getElementsByClassName("ks-left-paddle");
      var ksRightPaddle = document.getElementsByClassName("ks-right-paddle");

      // Total item and item size.
      var ksItemsLength = $(".ks-item").length;
      var ksItemSize = $(".ks-item").width();

      var ksPaddleMargin = 20;

      // Get slider div width.
      var ksGetMenuWrapperSize = function () {
        return $(".ks-menu-wrapper").outerWidth();
      };
      var ksMenuWrapperSize = ksGetMenuWrapperSize();

      // If window size is changed.
      $(window).on("resize", function () {
        ksMenuWrapperSize = ksGetMenuWrapperSize();
      });

      var ksMenuVisibleSize = ksMenuWrapperSize;

      // Total width of all menu items
      var ksGetMenuSize = function () {
        return ksItemsLength * ksItemSize + 60;
      };
      var ksMenuSize = ksGetMenuSize();
      var ksMenuInvisibleSize = ksMenuSize - ksMenuWrapperSize;

      var ksGetMenuPosition = function () {
        return $(".ks-menu").scrollLeft();
      };

      // Handle left-right paddle hide/show while scroll.
      $(".ks-menu").on("scroll", function () {
        ksMenuInvisibleSize = ksMenuSize - ksMenuWrapperSize;
        var ksMenuPosition = ksGetMenuPosition();
        var ksMenuEndOffset = ksMenuInvisibleSize - ksPaddleMargin;

        if (ksMenuPosition <= ksPaddleMargin) {
          $(ksLeftPaddle).addClass("hidden");
          $(ksRightPaddle).removeClass("hidden");
        } else if (ksMenuPosition < ksMenuEndOffset) {
          // show both paddles in the middle
          // Fixme: Need to be fixed this condition.
          $(ksLeftPaddle).removeClass("hidden");
          //                    $(ksRightPaddle).removeClass('hidden');
          $(ksRightPaddle).addClass("hidden");
        } else if (ksMenuPosition >= ksMenuEndOffset) {
          $(ksLeftPaddle).removeClass("hidden");
          $(ksRightPaddle).addClass("hidden");
        }
      });

      // Check visibility of the paddles.
      var ksMenuPosition_curr = ksGetMenuPosition();
      var ksMenuEndOffset_curr = ksMenuInvisibleSize - ksPaddleMargin;
      if (ksMenuPosition_curr > ksMenuEndOffset_curr) {
        $(ksLeftPaddle).addClass("hidden");
        $(ksRightPaddle).addClass("hidden");
      }

      $(ksRightPaddle).on("click", function () {
        var ksItemSize = $(".ks-item").width();
        var ksGetMenuSize = function () {
          return ksItemsLength * ksItemSize + ksItemSize * 2;
        };
        var ksMenuSize = ksGetMenuSize();
        var ksMenuWrapperSize = ksGetMenuWrapperSize();
        var ksMenuInvisibleSize = ksMenuSize - ksMenuWrapperSize;
        $(".ks-menu").animate(
          { scrollLeft: ksMenuInvisibleSize },
          ksScrollDuration
        );
      });

      $(ksLeftPaddle).on("click", function () {
        $(".ks-menu").animate({ scrollLeft: "0" }, ksScrollDuration);
      });
    },

    ks_disable_control_panel_buttons() {
      if (gantt.config.ks_disable_graph_overlay) {
        if (document.getElementById("ks_toggle_overlay")) {
          document.getElementById("ks_toggle_overlay").disabled = true;
        }
      }
    },

    //From UTC to Local Time Conversion
    ksConversionUtcToLocal: function (ksDate) {
      var ks_date = ksDate.clone();
      ks_date.add(session.getTZOffset(ksDate), "minutes");
      return ks_date.toDate();
    },

    on_detach_callback: function () {
      gantt.config.ks_show_resource_panel = false;
      $("button#ks_toggle_resource").removeClass("ks_control_active");
      this._super(...arguments);
    },

    ks_gantt_view_datetime_format: function () {
      gantt.config.ks_lang_datetime_format = time.getLangDatetimeFormat();
      gantt.ks_gantt_view_datetime_format = function (ks_input_datetime) {
        return moment(ks_input_datetime).format(
          gantt.config.ks_lang_datetime_format
        );
      };
    },

    ks_task_drag_and_drop: function () {
      gantt.config.order_branch = false;
      gantt.config.order_branch_free = false;
      if (
        this.state.groupedBy.length == 0 &&
        this.ks_model_name != "project.project"
      ) {
        gantt.config.order_branch = "marker";
        gantt.config.order_branch = true;
        if (this.ks_allow_subtasks) gantt.config.order_branch_free = true;
      }

      // Disable reorder from arch options
      if (this.ks_gantt_config && this.ks_gantt_config.ks_hide_task_reorder) {
        gantt.config.order_branch = false;
        gantt.config.order_branch_free = false;
      }

      // can't reorder task when group-by is enabled.
      gantt.config.ks_attached_events.push(
        gantt.attachEvent("onRowDragStart", function (id, target, e) {
          if (gantt.config.order_branch) return true;
          return false;
        })
      );
    },
  });

  return ksGanttRenderer;
});

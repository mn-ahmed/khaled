odoo.define("ks_gantt_view.Model", function (require) {
  "use strict";

  var AbstractModel = require("web.AbstractModel");
  var concurrency = require("web.concurrency");
  var session = require("web.session");
  var fieldUtils = require("web.field_utils");
  var core = require("web.core");

  var _t = core._t;

  var ksGanttModel = AbstractModel.extend({
    init: function () {
      this._super.apply(this, arguments);
      this.dp = new concurrency.DropPrevious();
    },

    load: function (params) {
      this.modelName = params.modelName;
      this.fields = params.fields;
      this.domain = params.domain;
      this.context = params.context;
      this.ks_export_field = params.ks_export_field;
      this.ks_requiredFields = params.ks_requiredFields;
      // Add arch fields.
      this.ks_gantt_arch = params.ks_gantt_arch;
      this.ks_gantt_link_info = params.ks_task_link_info
        ? params.ks_task_link_info
        : false;
      this.ks_defaultGroupBy = params.ks_defaultGroupBy
        ? [params.ks_defaultGroupBy]
        : [];
      if (!params.groupedBy || !params.groupedBy.length) {
        params.groupedBy = this.ks_defaultGroupBy;
      }
      this.ksDataForGantt = {
        groupedBy: params.groupedBy,
        name: params.name,
        fields: params.fields,
      };
      return this._ksComputeData().then(function () {
        return Promise.resolve();
      });
    },

    get: function (KsRowId) {
      return _.extend({}, this.ksDataForGantt);
    },

    //From Local Time to UTC Time Conversion
    conversionToUTCTime: function (ksDate) {
      var ks_date = ksDate.clone();
      if (!ks_date.isUTC()) {
        ks_date.subtract(session.getTZOffset(ksDate), "minutes");
      }
      return ks_date.format("YYYY-MM-DD HH:mm:ss");
    },

    //data fetch for display
    _ksComputeData: function () {
      var self = this;
      var KsFilter = this.domain;
      var ksGroupDefaultData;
      if (
        this.ksDataForGantt &&
        this.ksDataForGantt.groupedBy &&
        this.ksDataForGantt.groupedBy.length
      ) {
        // Remove date field group by.
        this.ksDataForGantt.groupedBy = _.filter(
          this.ksDataForGantt.groupedBy,
          function (ksGroupBy) {
            if (ksGroupBy.indexOf(":") < 0) return ksGroupBy;
          }
        );

        ksGroupDefaultData = this._rpc({
          model: this.modelName,
          method: "read_group",
          fields: this.ksFetchDefaultFields(),
          domain: KsFilter,
          context: _.extend(this.context, {
            group_by: this.ksDataForGantt.groupedBy,
          }),
          groupBy: this.ksDataForGantt.groupedBy,
          lazy: this.ksDataForGantt.groupedBy.length === 1,
        });
      }

      var ksDefaultData = this._rpc({
        route: "/web/dataset/search_read",
        model: this.modelName,
        fields: this.ksFetchDefaultFields(),
        context: _.extend(this.context, {
          group_by: this.ksDataForGantt.groupedBy,
        }),
        domain: KsFilter,
      });
      return this.dp
        .add(Promise.all([ksGroupDefaultData, ksDefaultData]))
        .then(function (results) {
          self.ksDataForGantt.records = [];
          self.ksDataForGantt.KsAllTaskIds = [];
          var ksTasksRecord = [];

          // Set group_by_records data.
          if (results && results[0] && results[0].length) {
            self.ksDataForGantt.ks_group_by_records = results[0];
            ksTasksRecord = results[0];
          }
          // Set all task data.
          if (results && results[1] && results[1].records) {
            self.ksDataForGantt.records = results[1].records;
            ksTasksRecord = results[1].records;
          }

          // Get All Tasks IDs to verify task's parent.
          ksTasksRecord.forEach((element) => {
            self.ksDataForGantt.KsAllTaskIds.push(element.id);
          });
        });
    },

    // Required field for fetching data
    ksFetchDefaultFields: function () {
      var ksRequireFiled = ["display_name"];
      if ("create" in this.ks_gantt_arch) {
        delete this.ks_gantt_arch["create"];
      }
      if ("ks_context" in this.ks_gantt_arch) {
        delete this.ks_gantt_arch["ks_context"];
      }
      ksRequireFiled = ksRequireFiled.concat(
        this.ksDataForGantt.groupedBy,
        Object.values(this.ks_gantt_arch)
      );
      ksRequireFiled = _.filter(ksRequireFiled, function (item) {
        return item != "ks_project_row";
      });
      // Adding create date to required data.
      if (ksRequireFiled.indexOf("create_date") < 0) {
        ksRequireFiled.push("create_date");
      }
      // Read field values which needs to export for json.
      if (this.ks_export_field && this.ks_export_field.length > 0) {
        ksRequireFiled = ksRequireFiled.concat(this.ks_export_field);
      }

      return _.uniq(ksRequireFiled);
    },

    // Reload page on data change
    reload: function (ksAnyObj, ksGetObj) {
      if (ksGetObj.groupBy) {
        this.ksDataForGantt.groupedBy = ksGetObj.groupBy;
      }
      if (ksGetObj.domain) {
        this.domain = ksGetObj.domain;
      }
      return this._ksComputeData().then(function () {
        return Promise.resolve();
      });
    },

    // function to update the task.
    /**
     * Update task parent.
     */
    updateTask: function (data) {
      var ks_data_values = {};
      var id = data.id;
      var gantt_date_obj = gantt.date.str_to_date("%d-%m-%Y %h:%i");
      var date_start = gantt_date_obj(data.start_date);
      var date_end = gantt_date_obj(data.end_date);
      if (data.constraint_date && this.ks_gantt_arch.ks_constraint_task_date) {
        var constraint_date = gantt_date_obj(data.constraint_date);
        ks_data_values[this.ks_gantt_arch.ks_constraint_task_date] =
          this.conversionToUTCTime(moment(constraint_date));
      }
      ks_data_values[this.ks_gantt_arch.ks_task_start_date] =
        this.fields[this.ks_gantt_arch.ks_task_start_date].type == "date"
          ? moment(date_start).format("YYYY-MM-DD")
          : this.conversionToUTCTime(moment(date_start));
      ks_data_values[this.ks_gantt_arch.ks_task_end_date] =
        this.fields[this.ks_gantt_arch.ks_task_end_date].type == "date"
          ? moment(date_end).format("YYYY-MM-DD")
          : this.conversionToUTCTime(moment(date_end));
      if (this.ks_gantt_arch.ks_constraint_task_type) {
        ks_data_values[this.ks_gantt_arch.ks_constraint_task_type] =
          data.constraint_type;
      }
      if (data.ks_task_model) {
        return this.ksUpdateProjectGanttTask(data);
      }
      return this._rpc({
        model: this.modelName,
        method: "write",
        args: [id, ks_data_values],
      });
    },

    ksUpdateProjectGanttTask: function (data) {
      var id = parseInt(data.id.split("_")[1]);
      var ks_data_values = {};
      var gantt_date_obj = gantt.date.str_to_date("%d-%m-%Y %h:%i");
      var date_start = gantt_date_obj(data.start_date);
      var date_end = gantt_date_obj(data.end_date);

      if (data.constraint_date && this.ks_gantt_arch.ks_constraint_task_date) {
        var constraint_date = gantt_date_obj(data.constraint_date);
        ks_data_values["ks_constraint_task_date"] = this.conversionToUTCTime(
          moment(constraint_date)
        );
      }

      ks_data_values["ks_start_datetime"] = this.conversionToUTCTime(
        moment(date_start)
      );
      ks_data_values["ks_end_datetime"] = this.conversionToUTCTime(
        moment(date_end)
      );
      if (data.ks_constraint_task_type) {
        ks_data_values["ks_constraint_task_type"] = data.constraint_type;
      }

      return this._rpc({
        model: data.ks_task_model,
        method: "write",
        args: [id, ks_data_values],
      });
    },

    /**
     * Update task parent.
     */
    ksUpdateParent: function (data) {
      var ks_data_values = {};
      var id = data.id;
      ks_data_values["parent_id"] = data[this.ks_gantt_arch.ks_parent_task];

      return this._rpc({
        model: this.modelName,
        method: "write",
        args: [id, ks_data_values],
      });
    },

    /*
     * Update Task Parent and Sequence.
     */
    ksUpdateParentSequence: function (data) {
      if (this.modelName == "project.project") {
        return false;
      }
      return this._rpc({
        model: this.modelName,
        method: "ks_update_task_sequence",
        args: [data],
      });
    },

    /**
     * Create task link.
     */
    ksCreateLink: function (data) {
      var create_dict = {
        ks_task_link_type: data.type,
      };
      if (this.modelName == "project.project") {
        create_dict["ks_source_task_id"] = parseInt(
          data.source.split("task_")[1]
        );
        create_dict["ks_target_task_id"] = parseInt(
          data.target.split("task_")[1]
        );
      } else {
        create_dict[this.ks_gantt_link_info.ks_link_source] = parseInt(
          data.source
        );
        create_dict[this.ks_gantt_link_info.ks_link_target] = parseInt(
          data.target
        );
      }
      return this._rpc({
        model: "ks.task.link",
        method: "create",
        args: [create_dict],
      }).then(
        function (results) {
          // after create link update gantt link id.
          gantt.changeLinkId(this.id, results);
        }.bind(data)
      );
    },

    /**
     * Delete task link
     */
    ksDeleteLink: function (data) {
      return this._rpc({
        model: "ks.task.link",
        method: "unlink",
        args: [[data.id]],
      });
    },

    //        /*
    //        * Function to update local dictionary (reason: if gantt needs to parse data without update, then it will not
    //        * show old data on the view).
    //        */
    //        ks_update_gantt_local_dict: function(data) {
    //            var ks_new_gantt_task_data = _.filter(gantt.config.ks_gantt_task_data["data"], function(ks_item){
    //                if (ks_item.id == data.id)
    //                    return data
    //                return ks_item;
    //            }.bind(data));
    //
    //            gantt.config.ks_gantt_task_data["data"] = ks_new_gantt_task_data;
    //        },
  });

  return ksGanttModel;
});

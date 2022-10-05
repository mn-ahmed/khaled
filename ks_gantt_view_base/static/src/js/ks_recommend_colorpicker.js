odoo.define("ks_gantt_view.ks_recommend_colorpicker", function (require) {
  "use strict";

  var ColorPickerWidget = require("web.Colorpicker");
  var field_registry = require("web.field_registry");
  var ColorPicker = require("web.basic_fields");

  var ks_gantt_color_picker_widget =
    ColorPickerWidget.ColorpickerWidget.include({
      events: _.extend(
        {},
        ColorPickerWidget.ColorpickerWidget.prototype.events,
        {
          "click div.ks_recommend_color": "_KsClickRecommendColor",
        }
      ),

      _KsClickRecommendColor: function (ev) {
        $(".o_colorpicker_widget input.o_hex_input")
          .val($(ev.currentTarget).attr("data-hex"))
          .trigger("change");
      },
    });

  var ks_gantt_color_picker = ColorPicker.FieldColor.extend({
    init: function (parent, options) {
      this.ks_gantt_color_widget = true;
      this._super(...arguments);
    },
  });

  field_registry.add("ks_gantt_color_picker", ks_gantt_color_picker);
  return {
    ks_gantt_color_picker: ks_gantt_color_picker,
    ks_gantt_color_picker_widget: ks_gantt_color_picker_widget,
  };
});

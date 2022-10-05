from odoo import api, fields, models, _


class KsHolidayGanttSettings(models.Model):
    _name = 'hr.leave.gantt.settings'
    _description = 'Gantt View Setting For Time Off'

    name = fields.Char(default='Time Off Gantt View Settings')
    ks_enable_dynamic_text = fields.Boolean(string='Dynamic Text',
                                            help="Enable/Disable Dynamic Text.", default=True)
    ks_enable_dynamic_progress = fields.Boolean(string='Dynamic Progress',
                                                help="Enable/Disable Dynamic Progress.", default=False)
    ks_holiday_stage_color_ids = fields.One2many(comodel_name='ks.holiday.gantt.stage.color', inverse_name='ks_holiday',
                                                 string='Stage Color')
    ks_enable_quickinfo_extension = fields.Boolean(string='Quick Info',
                                                   help="Enable/Disable Quick Info.", default=True)

    # Tooltip fields
    ks_tooltip_task_name = fields.Boolean(string='Title', default=True, help='Enable task name on tooltip')
    ks_tooltip_task_duration = fields.Boolean(string='Duration', default=True, help='Enable task duration on tooltip')
    ks_tooltip_task_start_date = fields.Boolean(string='Start Date', default=True,
                                                help='Enable task start date on tooltip')
    ks_tooltip_task_end_date = fields.Boolean(string='End Date', default=True, help='Enable task end date on tooltip')
    ks_tooltip_task_stage = fields.Boolean(string='Stage', default=True, help='Enable task stage on tooltip')

    @api.model
    def ks_get_gantt_view_settings(self):
        ks_gantt_settings = self.env.ref('ks_gantt_view_hr_holidays.ks_gantt_view_holidays_data_settings')

        ks_gantt_view_settings = {
            'ks_enable_task_dynamic_text': ks_gantt_settings.ks_enable_dynamic_text,
            'ks_enable_quickinfo_extension': ks_gantt_settings.ks_enable_quickinfo_extension,
        }

        # ks_tooltip_fields = ['ks_tooltip_task_name', 'ks_tooltip_task_duration', 'ks_tooltip_task_start_date',
        #                      'ks_tooltip_task_end_date', 'ks_tooltip_task_progress', 'ks_tooltip_task_stage',
        #                      'ks_tooltip_task_constraint_type', 'ks_tooltip_task_constraint_date',
        #                      'ks_tooltip_task_deadline']

        ks_tooltip_fields = ['ks_tooltip_task_name', 'ks_tooltip_task_duration', 'ks_tooltip_task_start_date',
                             'ks_tooltip_task_end_date', 'ks_tooltip_task_stage']

        ks_project_tooltip_config = {}
        for config_field in ks_tooltip_fields:
            ks_project_tooltip_config[config_field] = ks_gantt_settings[config_field]

        ks_gantt_view_settings['ks_project_tooltip_config'] = ks_project_tooltip_config
        return ks_gantt_view_settings

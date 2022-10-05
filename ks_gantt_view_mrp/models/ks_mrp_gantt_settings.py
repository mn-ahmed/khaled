from odoo import api, fields, models, _


class KsGanttMrp(models.Model):
    _name = 'mrp.gantt.settings'
    _description = 'Manufacturing Gantt Settings'

    name = fields.Char(default='Manufacturing Gantt View Settings')
    ks_enable_dynamic_text = fields.Boolean(string='Dynamic Text',
                                            help="Enable/Disable Dynamic Text.", default=True)
    ks_enable_quickinfo_extension = fields.Boolean(string='Quick Info',
                                                   help="Enable/Disable Quick Info.", default=True)

    # Tooltip fields for MO
    ks_tooltip_name_mo = fields.Boolean(string='Title', default=True, help='Enable name on tooltip')
    ks_tooltip_duration_mo = fields.Boolean(string='Duration', default=True, help='Enable duration on tooltip')
    ks_tooltip_start_date_mo = fields.Boolean(string='Start Date', default=True,
                                              help='Enable start date on tooltip')
    ks_tooltip_end_date_mo = fields.Boolean(string='End Date', default=True, help='Enable end date on tooltip')
    ks_tooltip_stage_mo = fields.Boolean(string='Stage', default=True, help='Enable stage on tooltip')

    ks_mo_stage_color_ids = fields.One2many(comodel_name='ks.mrp.gantt.stage.color', inverse_name='ks_gantt_setting',
                                            string='Stage Color')
    ks_tooltip_constraint_type_mo = fields.Boolean(string='Constraint Type', default=True,
                                                   help='Enable constraint type on tooltip')
    ks_tooltip_constraint_date_mo = fields.Boolean(string='Constraint Date', default=True,
                                                   help='Enable constraint date on tooltip')

    # Fields for work order
    ks_enable_dynamic_text_wo = fields.Boolean(string='Dynamic Text',
                                               help="Enable/Disable Dynamic Text.", default=True)
    ks_enable_quickinfo_extension_wo = fields.Boolean(string='Quick Info',
                                                      help="Enable/Disable Quick Info.", default=True)
    ks_enable_dynamic_progress_wo = fields.Boolean(string='Dynamic Progress',
                                                   help="Enable/Disable Dynamic Progress.", default=True)

    # Tooltip for work order
    ks_tooltip_name_wo = fields.Boolean(string='Title', default=True, help='Enable name on tooltip')
    ks_tooltip_duration_wo = fields.Boolean(string='Duration', default=True, help='Enable duration on tooltip')
    ks_tooltip_start_date_wo = fields.Boolean(string='Start Date', default=True,
                                              help='Enable start date on tooltip')
    ks_tooltip_end_date_wo = fields.Boolean(string='End Date', default=True, help='Enable end date on tooltip')
    ks_tooltip_progress_wo = fields.Boolean(string='Progress', default=True, help='Enable progress on tooltip')
    ks_tooltip_stage_wo = fields.Boolean(string='Stage', default=True, help='Enable stage on tooltip')

    ks_stage_color_wo_ids = fields.One2many(comodel_name='ks.mrp.gantt.stage.color.wo', inverse_name='ks_gantt_setting',
                                            string='Stage Color')

    @api.model
    def ks_get_gantt_view_mrp_settings(self):
        ks_gantt_settings = self.env.ref('ks_gantt_view_mrp.ks_gantt_mrp_data_settings')

        ks_gantt_view_settings = {
            'ks_enable_task_dynamic_text': ks_gantt_settings.ks_enable_dynamic_text,
            'ks_enable_quickinfo_extension': ks_gantt_settings.ks_enable_quickinfo_extension,
        }

        ks_tooltip_fields = ['ks_tooltip_name_mo', 'ks_tooltip_duration_mo', 'ks_tooltip_start_date_mo',
                             'ks_tooltip_end_date_mo', 'ks_tooltip_stage_mo', 'ks_tooltip_constraint_type_mo',
                             'ks_tooltip_constraint_date_mo']

        ks_tooltip_fields_dict = {
            'ks_tooltip_name_mo': 'ks_tooltip_task_name',
            'ks_tooltip_duration_mo': 'ks_tooltip_task_duration',
            'ks_tooltip_start_date_mo': 'ks_tooltip_task_start_date',
            'ks_tooltip_end_date_mo': 'ks_tooltip_task_end_date',
            'ks_tooltip_stage_mo': 'ks_tooltip_task_stage',
            'ks_tooltip_constraint_type_mo': 'ks_tooltip_task_constraint_type',
            'ks_tooltip_constraint_date_mo': 'ks_tooltip_task_constraint_date',
        }

        ks_project_tooltip_config = {}
        for config_field in ks_tooltip_fields:
            ks_project_tooltip_config[ks_tooltip_fields_dict[config_field]] = ks_gantt_settings[config_field]

        ks_gantt_view_settings['ks_project_tooltip_config'] = ks_project_tooltip_config
        return ks_gantt_view_settings

    @api.model
    def ks_get_gantt_view_mrp_settings_wo(self):
        ks_gantt_settings = self.env.ref('ks_gantt_view_mrp.ks_gantt_mrp_data_settings')

        ks_gantt_view_settings = {
            'ks_enable_task_dynamic_text': ks_gantt_settings.ks_enable_dynamic_text_wo,
            'ks_enable_quickinfo_extension': ks_gantt_settings.ks_enable_quickinfo_extension_wo,
            'ks_enable_task_dynamic_progress': ks_gantt_settings.ks_enable_dynamic_progress_wo,
        }

        ks_tooltip_fields = ['ks_tooltip_name_wo', 'ks_tooltip_duration_wo', 'ks_tooltip_start_date_wo',
                             'ks_tooltip_end_date_wo', 'ks_tooltip_stage_wo', 'ks_tooltip_progress_wo']

        ks_tooltip_fields_dict = {
            'ks_tooltip_name_wo': 'ks_tooltip_task_name',
            'ks_tooltip_duration_wo': 'ks_tooltip_task_duration',
            'ks_tooltip_start_date_wo': 'ks_tooltip_task_start_date',
            'ks_tooltip_end_date_wo': 'ks_tooltip_task_end_date',
            'ks_tooltip_stage_wo': 'ks_tooltip_task_stage',
            'ks_tooltip_progress_wo': 'ks_tooltip_task_progress'
        }

        ks_project_tooltip_config = {}
        for config_field in ks_tooltip_fields:
            ks_project_tooltip_config[ks_tooltip_fields_dict[config_field]] = ks_gantt_settings[config_field]

        ks_gantt_view_settings['ks_project_tooltip_config'] = ks_project_tooltip_config
        return ks_gantt_view_settings

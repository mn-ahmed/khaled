import logging
import json

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class KsMrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    ks_progress = fields.Char(compute="_compute_workorder_progress")
    ks_task_link_ids = fields.One2many(
        comodel_name='ks.task.link',
        inverse_name='ks_source_wo_id',
        string='Task links')
    ks_task_link_json = fields.Char(compute="ks_compute_json_data_task_link")
    ks_stage_color = fields.Char(compute='ks_compute_order_color')

    def _compute_workorder_progress(self):
        for rec in self:
            duration_count = 0
            for time_track in rec.time_ids:
                duration_count += time_track.duration
            if rec.duration_expected:
                rec.ks_progress = duration_count / rec.duration_expected * 100
            else:
                rec.ks_progress = 0

    def ks_compute_json_data_task_link(self):
        for rec in self:
            ks_task_link_json = []
            for task_link in rec.ks_task_link_ids:
                ks_task_link_json.append(
                    {
                        'id': task_link.id,
                        'source': task_link.ks_source_wo_id.id,
                        'target': task_link.ks_target_wo_id.id,
                        'type': task_link.ks_task_link_type,
                    }
                )
            rec.ks_task_link_json = json.dumps(ks_task_link_json)

    def ks_compute_order_color(self):
        """
        Function to compute order color.
        :return:
        """
        ks_gantt_setting = self.env.ref('ks_gantt_view_mrp.ks_gantt_mrp_data_settings')
        for rec in self:
            ks_stage_color = self.env['ks.mrp.gantt.stage.color.wo'].search(
                [('ks_state', '=', rec.state), ('ks_gantt_setting', '=', ks_gantt_setting.id)], limit=1)
            if ks_stage_color and ks_stage_color.ks_color:
                rec.ks_stage_color = ks_stage_color.ks_color
            else:
                rec.ks_stage_color = '#7C7BAD'

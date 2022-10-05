from odoo import api, exceptions, fields, models, _


class KsGanttViewStage(models.Model):
    _inherit = 'project.task.type'
    ks_stage_color = fields.Char('Stage Color')

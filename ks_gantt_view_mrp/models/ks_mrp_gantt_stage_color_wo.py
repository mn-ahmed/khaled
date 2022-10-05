from odoo import api, fields, models, _


class KsMRPGanttStageColor(models.Model):
    _name = 'ks.mrp.gantt.stage.color.wo'
    _description = 'MRP State Color For Gantt View Work Order'
    _sql_constraints = [
        ('unique_code', 'unique (ks_state)', "State can't be duplicated.")
    ]

    ks_state = fields.Selection([
        ('pending', 'Waiting for another WO'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='State', required='True')

    ks_color = fields.Char('Stage Color')
    ks_gantt_setting = fields.Many2one(comodel_name='mrp.gantt.settings')

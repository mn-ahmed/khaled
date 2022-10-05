from odoo import api, fields, models, _


class KsMRPGanttStageColor(models.Model):
    _name = 'ks.mrp.gantt.stage.color'
    _description = 'MRP Stage Color For Gantt View'
    _sql_constraints = [
        ('unique_code', 'unique (ks_state)', "State can't be duplicated.")
    ]

    ks_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State', required='True')

    ks_color = fields.Char('Stage Color')
    ks_gantt_setting = fields.Many2one(comodel_name='mrp.gantt.settings')

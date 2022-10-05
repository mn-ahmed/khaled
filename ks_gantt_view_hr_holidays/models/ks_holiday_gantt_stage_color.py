from odoo import api, fields, models, _


class KsHolidayGanttStageColor(models.Model):
    _name = 'ks.holiday.gantt.stage.color'
    _description = 'Time Off Stage Color For Gantt View'
    _sql_constraints = [
        ('unique_code', 'unique (ks_state)', 'Stage color must be unique.')
    ]

    ks_state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
        ], string='Status', required='True')

    ks_color = fields.Char('Stage Color')
    ks_holiday = fields.Many2one(comodel_name='hr.leave.gantt.settings')

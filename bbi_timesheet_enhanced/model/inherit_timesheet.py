from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError



class HrInheritTimesheetCost(models.Model):
    _inherit = 'hr.employee.public'

    timesheet_cost = fields.Monetary('Timesheet Cost', currency_field='currency_id',default=0.0)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

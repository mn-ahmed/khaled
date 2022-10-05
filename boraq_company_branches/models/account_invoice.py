from odoo import api, fields, models, tools, _

class AccountInvoice(models.Model):
    _inherit = "account.move"
    _description = 'Account Invoice'

    branch_id = fields.Many2one('company.branches', string='Branch', domain="[('company_id','=',company_id)]")

    
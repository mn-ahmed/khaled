from odoo import api, fields, models, tools, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    branch_id = fields.Many2one('company.branches', string='Branch', domain="[('company_id','=',company_id)]")
    

from odoo import api, fields, models, tools, _

class Company(models.Model):
    _inherit = "res.company"
    _description = 'Companies'

    branch_ids = fields.One2many('company.branches', string='Branches',inverse_name='company_id')

    
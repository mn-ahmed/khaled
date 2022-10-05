from odoo import fields, models


class KsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('ks_gantt', "Gantt")], ondelete={'ks_gantt': 'cascade'})

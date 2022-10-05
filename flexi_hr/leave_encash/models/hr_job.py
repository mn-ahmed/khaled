

from odoo import api, fields, models, _


class hr_job(models.Model):
    _inherit = 'hr.job'

    encash_leave = fields.Float(string="Encash Leave")


# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_important = fields.Boolean(related='project_id.is_important', string='Is Important project')
    from_time = fields.Float(string='From')
    to_time = fields.Float(string='To')

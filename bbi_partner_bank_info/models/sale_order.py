# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def compute_bank_note_from_partner(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.bank_info:
                    rec.note = rec.partner_id.bank_info

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class AccountMove(models.Model):
    _inherit = "account.move"

    bank_note = fields.Boolean(compute='compute_invoice_internal_note')

    @api.onchange('partner_id')
    def compute_bank_note_from_partner(self):
        for rec in self:
            if rec.partner_id:
                if rec.partner_id.bank_info:
                    rec.narration = rec.partner_id.bank_info

    @api.depends('partner_id')
    def compute_invoice_internal_note(self):
        for rec in self:
            rec.bank_note = False
            if rec.partner_id:
                if rec.partner_id.bank_info:
                    rec.narration = rec.partner_id.bank_info

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class ProjectPaymentTerm(models.Model):
    _name = "project.payment.term"

    sale_order_id = fields.Many2one('sale.order')
    currency_id = fields.Many2one(related='sale_order_id.currency_id')
    batch_number = fields.Char('Batch Name')
    percentage = fields.Integer('Percentage(%)')
    total_butch_amount = fields.Float('Total Batch Amount', compute='_compute_total_butch_amount', store=True)

    @api.depends('percentage')
    def _compute_total_butch_amount(self):
        for rec in self:
            rec.total_butch_amount = 0.0
            if rec.percentage:
                if rec.percentage > 100:
                    raise ValidationError(_('The Percentage per batch number cannot exceed 100 %'))
                rec.total_butch_amount = (rec.sale_order_id.amount_untaxed * rec.percentage) / 100

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    project_payment_term_ids = fields.One2many('project.payment.term', 'sale_order_id', string='Project Payment Term')
    project_cost = fields.Float('Project Cost')

    @api.model
    def create(self, vals):
        sale_obj = super(SaleOrder, self).create(vals)
        total_percentage = 0
        if sale_obj.project_payment_term_ids:
            if len(sale_obj.project_payment_term_ids) > 4:
                raise ValidationError(_("The project payment terms lines can't more than four batches %"))
            for line in sale_obj.project_payment_term_ids:
                total_percentage += line.percentage
        if total_percentage > 100:
            raise ValidationError(_('The total percentage for project payment terms cannot exceed 100 %'))
        return sale_obj

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        total_percentage = 0
        if self.project_payment_term_ids:
            if len(self.project_payment_term_ids) > 4:
                raise ValidationError(_("The project payment terms lines can't more than four batches %"))
            for line in self.project_payment_term_ids:
                total_percentage += line.percentage
        if total_percentage > 100:
            raise ValidationError(_('The total percentage for project payment terms cannot exceed 100 %'))
        return res

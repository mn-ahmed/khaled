# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"
    
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv,self)._create_invoice(order,so_line,amount)
        invoice.write({'branch_id':order.branch_id.id})
        return invoice
    
    
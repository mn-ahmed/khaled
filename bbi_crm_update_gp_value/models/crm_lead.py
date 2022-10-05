# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmOpportunity(models.Model):
    _inherit = "crm.lead"

    custom_gp_value = fields.Monetary('GP Value', currency_field='company_currency',
                                      compute='set_values_custom_gp_value')

    @api.depends('gp_percentage', 'cost')
    def set_values_custom_gp_value(self):
        for rec in self:
            # if rec.gp_percentage and rec.expected_revenue:
            rec.custom_gp_value = (rec.expected_revenue - rec.cost)

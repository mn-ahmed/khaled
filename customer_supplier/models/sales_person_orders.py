# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    contact_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier'), ('both', 'Both')], string='Contact Type')

   

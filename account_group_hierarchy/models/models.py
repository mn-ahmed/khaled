# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class addson/account_parent(models.Model):
#     _name = 'addson/account_parent.addson/account_parent'
#     _description = 'addson/account_parent.addson/account_parent'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

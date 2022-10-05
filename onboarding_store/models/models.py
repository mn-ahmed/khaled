# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError

#
# class onboardingStoreESS(models.Model):
#     _inherit = 'onboarding.proccess'
#
#     onboarding_offboarding = fields.Boolean(string='onboarding offboarding', default=False)
#
#     @api.multi
#     def laptop_delivered(self):
#         flag = self.env['res.users'].has_group('employees_self_services.onboarding_cycle_it_lead')
#         if flag and self.laptop:
#             self.laptop.state = 'used'
#             self.onboarding_offboarding = False
#         else:
#             if not flag:
#                 raise ValidationError("You don't have a permission")
#             elif not self.laptop:
#                 raise ValidationError("Please select laptop!")
#

class onboarding_store(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    _sql_constraints = [
        ('model_code_unique', 'unique(model_code)',
         _("A Model code can only be assigned to one product !")),
    ]

    model_code = fields.Char('Model Code')
    # onboarding_request = fields.Many2one('onboarding.proccess', compute='_employee_laptop')
    employee_device = fields.Many2one('hr.employee.public', compute='_employee_laptop_com')
    state = fields.Selection([
        ('available', 'Available'),
        ('preparing', 'Preparing'),
        ('maintenance', 'Maintenance'),
        ('used', 'Used')],
        default='available')
    device_cpu = fields.Char('CPU')
    device_ram = fields.Char('RAM')
    device_hd = fields.Char('Hard Desk')

    def _employee_laptop_com(self):
        for rec in self:
            if rec.type == 'product':
                onboarding_request = self.env['onboarding.proccess'].search([('laptop.id', '=', rec.id)], limit=1)
                if not onboarding_request.onboarding_offboarding:
                    rec.employee_device = onboarding_request.employee_id.id
                else:
                    rec.employee_device = False
            else:
                rec.employee_device = False

    def preparing_stage(self):
        self.state = 'preparing'

    def maintenance_stage(self):
        self.state = 'maintenance'

    def used_stage(self):
        self.state = 'used'

    def available_stage(self):
        self.state = 'available'



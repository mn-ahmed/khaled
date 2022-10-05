# -*- coding: utf-8 -*-

from odoo import models, fields, api , exceptions
# from odoo.odoo.exceptions import ValidationError


class hiringResigning(models.Model):
    _inherit = 'hr.employee'

    emp_id = fields.Char(string='Employee ID', groups="hr.group_hr_user")
    hiring = fields.Date(string="Hiring Date", groups="hr.group_hr_user")
    resign = fields.Date(string='Resigning Date', groups="hr.group_hr_user")
    children_bool = fields.Boolean(string='Children', groups="hr.group_hr_user")
    military_stat = fields.Many2one("military.status", string='Military Status', groups="hr.group_hr_user")
    military_cer = fields.Char('Military Certificate No ', groups="hr.group_hr_user")
    military_exp = fields.Date(string='Military Expire Date', groups="hr.group_hr_user")

    overtime = fields.Boolean(string='Eligible for overtime', groups="hr.group_hr_user")
    contract_type = fields.Many2one('hr.contract.type', string='Contract Type', groups="hr.group_hr_user")
    payment_type = fields.Many2one('hr.payment.type', string='Payment Type', groups="hr.group_hr_user")

    visa_date = fields.Date(string='Visa Issue date', groups="hr.group_hr_user")
    


   








    @api.constrains('visa_expire')
    def _check_dob(self):
        for record in self:
            if record.visa_date and record.visa_expire <= record.visa_date:
                        raise exceptions.ValidationError("Your Visa Expiry Date less then Visa Issue date")


class MilitaryStatus(models.Model):
    _name = "military.status"

    name = fields.Char(string='Status Name',required=True)


class PaymentType(models.Model):
    _name = 'hr.payment.type'

    name = fields.Char(string='Payment Type', required=True)







#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
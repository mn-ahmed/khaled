# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta




class InheritOnboardingRequest(models.Model):
    _inherit = 'onboarding.proccess'

    employee_type = fields.Selection([
        ('fte', "FTE"),
        ('ots', "OTS")], string="Employee Type")
    personal_email = fields.Char("Personal Email")
    employee_bank_account = fields.Selection([
        ('create_acc', 'Create Account'),
        ('cib', "CIB"),
        ('qnb', "QNB"),
        ], string="Bank Account", default='create_acc')

    bank_account_no = fields.Char("Account Number")
    client_id = fields.Integer('Client ID')
    branch_code = fields.Integer("Branch Code")
    account_holder_name = fields.Char("Account Holder Name")
    contract_type = fields.Selection([
        ('fte_egypt', "FTE Egypt"),
        ('offshore_egypt', "Offshore Egypt"),
        ('international', "International"),
        ('ots', "OTS"),
        ('intern', "Intern"),
        ('part_time', "Part-Time")
    ], string="Contract Type", track_visibility='onchange')

    @api.depends('start_date')
    def compute_leave_balance(self):
        for rec in self:
            if rec.start_date and rec.contract_type in ['fte_egypt', 'offshore_egypt', 'international', 'ots']:
                # today = fields.Datetime.now()
                # months = (today.year - rec.start_date.year)*12 + today.month - rec.start_date.month

                months = 12 - rec.start_date.month
                print(months, 'monthsssss')
                rec.leave_opening_balance = (months + 1) * 1.75
            elif rec.contract_type in ['intern', 'part_time']:
                rec.leave_opening_balance = 0
            else:
                rec.leave_opening_balance = 0

    def update_employee_info(self):
        if self.employee_id:
            if self.email or self.personal_email or self.sim_card or self.gender or self.title or self.employee_manager or self.employee_department:
                print(self.employee_id)
                self.employee_id.sudo().write({'private_email': self.personal_email or self.employee_id.private_email,
                                               'work_phone': self.sim_card or self.employee_id.work_phone,
                                               'job_title': self.title.name or self.employee_id.job_title,
                                               'parent_id': self.employee_manager.id or self.employee_id.parent_id.id ,
                                               'department_id': self.employee_department or self.employee_id.department_id.id,
                                               'gender': self.gender or self.employee_id.gender,
                                               'work_email': self.email or self.employee_id.work_email,

                                               })


    def pass_to_d_manager(self):
        res = super(InheritOnboardingRequest, self).pass_to_d_manager()
        if self.employee_bank_account and self.employee_bank_account == "cib":
            if not self.bank_account_no and not self.account_holder_name:
                raise ValidationError("Please insert account number and account holder name.")
            else:
                bank_name = self.env['res.bank'].browse(34)
                self.employee_id.bank_account_id = self.env['res.partner.bank'].create({
                    'partner_id': self.employee_id.address_home_id.id,
                    'acc_number': self.bank_account_no,
                    'bank_id': bank_name.id,
                    'acc_holder_name': self.account_holder_name})

                print(self.employee_id.bank_account_id)
        elif self.employee_bank_account and self.employee_bank_account == "qnb":
            if not self.bank_account_no and not self.account_holder_name and not self.client_id and not self.branch_code:
                raise ValidationError("Please insert account number, account holder name,client ID and Branch Code.")
            else:
                bank_name = self.env['res.bank'].browse(35)
                self.employee_id.bank_account_id = self.env['res.partner.bank'].create({
                    'partner_id': self.employee_id.address_home_id.id,
                    'acc_number': self.bank_account_no,
                    'bank_id': bank_name.id,
                    'acc_holder_name': self.account_holder_name,
                    'client_id': self.client_id,
                    'branch_code': self.branch_code})
        return res



# class LeavesInherit(models.Model):
#     _inherit = "hr.leave"
#
#     @api.model
#     def create(self, vals):
#         result = super(LeavesInherit, self).create(vals)
#         leave_start_d = result.employee_id.hiring + relativedelta(months=2)
#         # request_day = datetime.date.today()
#         if result.employee_id.hiring and fields.Date.today() < leave_start_d:
#             raise ValidationError("Sorry, you can't submit a leave before 3 months from your hiring ")
#         return result


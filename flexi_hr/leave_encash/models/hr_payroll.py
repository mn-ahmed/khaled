

from odoo import api, fields, models, _


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    encash_leave = fields.Float(string="Encash Leave", compute='compute_salary_encash_leave')
    encash_amt = fields.Float(string="Encash Amount", compute='compute_salary_encash_leave')

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_salary_encash_leave(self):

        leave_to_encash = self.env['leave.encash'].search([
                        ('employee_id', '=', self.employee_id.id),
                        ('state', '=', 'approved'),
                        ('date', '>=', self.date_from),
                        ('date', '<=', self.date_to)
                        ])
        for encash in leave_to_encash:
            self.encash_leave += encash.leave_carry
            self.encash_amt += encash.amount

    @api.multi
    def action_payslip_done(self):
        res = super(hr_payslip, self).action_payslip_done()
        if self.state == 'done':
            leave_to_encash = self.env['leave.encash'].search([
                            ('employee_id', '=', self.employee_id.id),
                            ('state', '=', 'approved'),
                            ('date', '>=', self.date_from),
                            ('date', '<=', self.date_to)
                            ])
            for encash in leave_to_encash:
                    encash.state = 'paid'
                    encash.payslip_id = self.id



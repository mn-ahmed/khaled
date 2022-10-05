# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning



class License(models.Model):
    _name = 'domain.license'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Name', required=True, track_visibility='always')
    amount = fields.Integer(string='Amount')


class LicenseRequest(models.Model):
    _name = 'license.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee = fields.Many2one('hr.employee', string="Employee", track_visibility='always', required=True)
    employee_email = fields.Char(string='Email', related='employee.user_id.login')
    license_type = fields.Many2one('domain.license', string='License', required=True)
    # reject_reason = fields.Text(string='Reject Reason')
    # active = fields.Boolean(string='Active', default=False)
    state = fields.Selection([
        ('processing', "In Process"),
        ('active', "Active"),
        ('cancel', "Cancel")
    ], default='processing', string="Stage", track_visibility='onchange')

    # @api.multi
    # def reject(self, **additional_values):
    #     template = self.env.ref('medical_addition.mail_template_reject_medical_addition')
    #     self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
    #     print(self.hr_man)
    #     return self.write({'state': 'rejected',
    #                        'reject_reason': additional_values.get('reject_reason')})

    def done(self):
        # template = self.env.ref('medical_addition.mail_template_done_medical_addition')
        # self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.license_type.amount -= 1
        self.write({'state': 'active',
                    })

    def license_deactivate(self):
        self.license_type.amount += 1
        self.write({'state': 'cancel',
                    })

    def unlink(self):
        for rec in self:
            if rec.state == 'active':
                raise UserError(_(
                    'You cannot delete ,you can cancel it'))
            else:
                raise UserError(_(
                    'You cannot delete license request'))
        return super(LicenseRequest, self).unlink()
    # @api.model
    # def get_email_to(self):
    #     # user = self.env['res.users'].search(
    #     #     [('groups_id', '=', self.env.ref('embassy_letter.embassy_letter_approve_group').id)])
    #     user_group = self.env.ref("medical_addition.medical_addition_approve_group")
    #     email_list = [
    #         usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
    #     return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('license.request') or '/'
            vals['name'] = seq
        res = super(LicenseRequest, self).create(vals)
        # template = self.env.ref('medical_addition.mail_template_wfa_medical_addition')
        # self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res


# class RejectMessageMedicalAddition(models.TransientModel):
#     _name = 'reject.message.license'
#
#     reject_reason = fields.Text('Reject Reason')
#
#     def action_reject_reason(self):
#         medical_addition = self.env['medical.addition'].browse(self.env.context.get('active_ids'))
#         return medical_addition.reject(reject_reason=self.reject_reason)


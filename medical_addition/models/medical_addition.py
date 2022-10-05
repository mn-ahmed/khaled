# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_


class MedicalAddition(models.Model):
    _name = 'medical.addition'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee = fields.Many2one('hr.employee', string="Employee", track_visibility='always', readonly=True ,required=True, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    employee_full_name = fields.Char(string="Employee Full Name", related='employee.employee_full_name', store=True)
    add_wife = fields.Boolean(default=False, string='Add Wife')
    personal_image = fields.Binary(string="Personal Image", attachment=True, required=True)
    marriage_contract = fields.Binary(string="Marriage Contract", attachment=True)
    birthday = fields.Date('Date of Birth', related='employee.birthday', store=True)

    # personal_photo = fields.Binary("Favicon", attachment=True, required=True)

    reject_reason = fields.Text(string='Reject Reason')

    state = fields.Selection([
        ('wfa', "Waiting For Approve"),
        ('hr', "HR Department"),
        ('rejected', "Rejected"),
        ('done', "Done")
    ], default='wfa', string="Stage", track_visibility='onchange')

    # @api.multi
    def hr_department(self):
        self.state = 'hr'

    # @api.multi
    def reject(self, **additional_values):
        template = self.env.ref('medical_addition.mail_template_reject_medical_addition')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        print(self.hr_man)
        return self.write({'state': 'rejected',
                           'reject_reason': additional_values.get('reject_reason')})

    # @api.multi
    def done(self):
        template = self.env.ref('medical_addition.mail_template_done_medical_addition')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'done'

    @api.model
    def get_email_to(self):
        # user = self.env['res.users'].search(
        #     [('groups_id', '=', self.env.ref('embassy_letter.embassy_letter_approve_group').id)])
        user_group = self.env.ref("medical_addition.medical_addition_approve_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('medical.addition') or '/'
            vals['name'] = seq
        res = super(MedicalAddition, self).create(vals)
        template = self.env.ref('medical_addition.mail_template_wfa_medical_addition')
        self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res


class RejectMessageMedicalAddition(models.TransientModel):
    _name = 'reject.message.medical.addition'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        medical_addition = self.env['medical.addition'].browse(self.env.context.get('active_ids'))
        return medical_addition.reject(reject_reason=self.reject_reason)


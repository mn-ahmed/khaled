# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, Warning


class Resignation(models.Model):
    _name = 'resignation.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False,  index=True, readonly=True,default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee',readonly=True,string="Employee", track_visibility='always',
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)],limit=1))

    employee_full_name = fields.Char(string="Employee Full Name",related='employee_name.employee_full_name')
    employee_direct_manager = fields.Many2one('hr.employee', string="Direct Manager", related='employee_name.parent_id')
    employee_project_manager = fields.Many2one('hr.employee', string="Project Manager", related='employee_name.employee_project_manager' )
    employee_project = fields.Many2many('employee.project', string="Project", related='employee_name.employee_project')
    employee_email = fields.Char(string="Email",related='employee_name.work_email' )
    last_date = fields.Date(string='Suggested Last day In BBI', required=True, track_visibility='onchange')
    reason = fields.Text(string='Leave Reason', required=True)

    d_comment = fields.Text(string='DM Comment')
    hr_comment = fields.Text(string='HR Comment')
    bbi_last_date = fields.Date(string='Final Last day In BBI', track_visibility='onchange')

    reject_reason = fields.Text(string='Reject Reason')

    state = fields.Selection([
        ('draft', "Draft"),
        ('sent', "Sent"),
        ('dm', "DM Approve"),
        ('hr', "HR Approve"),
        ('rejected', "Rejected"),
    ], default='draft', string="Stage", track_visibility='onchange')

    def unlink(self):
        for resign in self:
            flag = self.env['res.users'].has_group('base.group_system') or self.env['res.users'].has_group('base.group_erp_manager')
            if not flag:
                if resign.state != 'draft':
                    raise UserError(
                        'You cannot delete a resignation request')
            else:
                return super(Resignation, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('resignation.request') or '/'
            vals['name'] = seq
        res = super(Resignation, self).create(vals)
        return res

    def sent_request(self):
        self.state = 'sent'
        template = self.env.ref('offboarding.mail_template_resignation_request_direct_manager_mail')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

    def dm_approve(self):
        if self.env.user == self.employee_name.user_id:
            raise ValidationError("Please, You Can't Approve Your request ")
        else:
            self.state = 'dm'
            template = self.env.ref('offboarding.mail_template_resignation_request_hr_mail')
            # self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

    def hr_approve(self):
        if self.env.user == self.employee_name.user_id:
            raise ValidationError("Please, You Can't Approve Your request ")
        else:
            self.state = 'hr'
            self.env['offboarding.request'].sudo().create({
                'employee_name': self.employee_name.id,
                'employee_full_name': self.employee_full_name,
                'employee_direct_manager': self.employee_direct_manager.id,
                'employee_project_manager': self.employee_project_manager.id,
                'employee_project': self.employee_project,
                'employee_email': self.employee_email,
                'bbi_last_date': self.bbi_last_date,})
            template = self.env.ref('offboarding.mail_template_resignation_request_user_approve_mail')
            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

    def resubmit(self):
        self.state = 'sent'

    def reject(self, **additional_values):
        self.write({'state': 'rejected',
                    'reject_reason': additional_values.get('reject_reason')})
        template = self.env.ref('offboarding.mail_template_resignation_request_user_reject_mail')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

    @api.model
    def get_email_to_hr(self):
        user_group = self.env.ref("offboarding.resignation_request_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)


class RejectMessageAccessCard(models.TransientModel):
    _name = 'reject.message.resignation'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        resignation = self.env['resignation.request'].browse(self.env.context.get('active_ids'))
        return resignation.reject(reject_reason=self.reject_reason)


# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_


class HRLetter(models.Model):
    _name = 'experience.letter'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string="Employee", track_visibility='always', readonly=True,
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    department_name = fields.Many2one('hr.department', related='employee_name.department_id')
    hiring_date = fields.Date('Hiring Date', related='employee_name.hiring')
    job_title = fields.Char('Job Title', related='employee_name.job_title')

    create_date = fields.Date(string='Created On', default=fields.Date.today(), readonly=True)
    reject_reason = fields.Text(string='Reject Reason')

    # hr_man = fields.Many2many('res.users', string='hr man', domain=lambda self: [('groups_id', 'in', self.env.ref('hr_letter.hr_letter_approve_group').id)])

    state = fields.Selection([
        ('wfa', "Waiting For Approve"),
        ('hr', "HR Department"),
        ('rejected', "Rejected"),
        ('done', "Done")
    ], default='wfa', string="Stage", track_visibility='onchange')

    def hr_department(self):
        self.state = 'hr'

    def reject(self, **additional_values):
        template = self.env.ref('ess_requests.mail_template_reject_experience_letter')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

        return self.write({'state': 'rejected',
                           'reject_reason': additional_values.get('reject_reason')})

    def done(self):
        template = self.env.ref('ess_requests.mail_template_done_experience_letter')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'done'

    @api.model
    def get_email_to(self):
        user_group = self.env.ref("ess_requests.hr_experience_letter_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('experience.letter') or '/'
            vals['name'] = seq
        res = super(HRLetter, self).create(vals)
        template = self.env.ref('ess_requests.mail_template_experience_letter')
        self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res


class RejectMessageHR(models.TransientModel):
    _name = 'reject.message.experience.letter'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        experience_letter = self.env['experience.letter'].browse(self.env.context.get('active_ids'))
        return experience_letter.reject(reject_reason=self.reject_reason)


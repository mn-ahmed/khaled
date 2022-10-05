# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_


class HRLetter(models.Model):
    _name = 'hr.letter'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string="Employee", track_visibility='always', readonly=True,
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    create_date = fields.Datetime(string='Created On', default=fields.Datetime.now, readonly=True)
    direction_of_letter = fields.Char(string='Direction of letter', required=True)
    reason = fields.Char(string='Reason', required=True)
    note = fields.Text(string="Note", track_visibility='always')
    reject_reason = fields.Text(string='Reject Reason')
    # users = fields.Many2one('res.users', string="hr man",
    #                         domain=lambda self: self.env['res.users'].search([('groups_id', '=',self.env.ref('hr_letter.hr_letter_approve_group').id)]))

    # @api.depends("state")
    # def compute_hr_man(self):
    #     for rec in self:
    #         user = self.env['res.users'].search(
    #             [('groups_id', '=', rec.env.ref('hr_letter.hr_letter_approve_group').id)])
    #         if user:
    #             rec.hr_man = user

    hr_man = fields.Many2many('res.users', string='hr man', domain=lambda self: [('groups_id', 'in', self.env.ref('hr_letter.hr_letter_approve_group').id)])
    # hr_man = fields.Many2one('res.users', string='hr man', domain=_compute_hr_man) # compute='_compute_hr_man', store=True , ,default=lambda self: self.env['res.users'].has_group('hr_letter.hr_letter_approve_group')

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
        template = self.env.ref('hr_letter.mail_template_reject_hr_letter')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        print(self.hr_man)
        return self.write({'state': 'rejected',
                           'reject_reason': additional_values.get('reject_reason')})

    # @api.multi
    def done(self):
        template = self.env.ref('hr_letter.mail_template_done_hr_letter')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'done'

    @api.model
    def get_email_to(self):
        # user = self.env['res.users'].search(
        #     [('groups_id', '=', self.env.ref('embassy_letter.embassy_letter_approve_group').id)])
        user_group = self.env.ref("hr_letter.hr_letter_approve_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('hr.letter') or '/'
            vals['name'] = seq
        # user = self.env['res.users'].search([('groups_id', '=', self.env.ref('hr_letter.hr_letter_approve_group').id)])
        # vals['hr_man'] = user
        res = super(HRLetter, self).create(vals)
        template = self.env.ref('hr_letter.mail_template_wfa_hr_letter')
        self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res


class RejectMessageHR(models.TransientModel):
    _name = 'reject.message.hr'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        hr_letter = self.env['hr.letter'].browse(self.env.context.get('active_ids'))
        return hr_letter.reject(reject_reason=self.reject_reason)


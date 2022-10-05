# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_


class EmbassyLetter(models.Model):
    _name = 'embassy.letter'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                                 required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string="Employee", track_visibility='always', readonly=True,
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    employee_name_passport = fields.Char(string="Passport Employee Name",  required=True,)
    embassy_country = fields.Many2one('res.country', string='Country', required=True)
    date_from = fields.Date(string='Date From', required=True, track_visibility='always')
    date_to = fields.Date(string='Date To',  required=True, track_visibility='always')
    create_date = fields.Datetime(string='Created On', default=fields.Datetime.now, readonly=True)
    passport_number = fields.Char(string="Passport Number", required=True)
    passport_issue_date = fields.Date(string='Passport Issue Date', required=True)
    passport_expiry_date = fields.Date(string='Passport Expiry Date', required=True)
    note = fields.Text(string="Note", track_visibility='always')
    visa_duration = fields.Char(string="Visa Duration")
    visa_type = fields.Many2one('visa.type', string='Visa Type', track_visibility='always')
    travel_nature = fields.Many2one('travel.nature', string='Travel Nature', track_visibility='always')
    reject_reason = fields.Text(string='Reject Reason')
    hr_man = fields.Many2many('res.users', string='hr man', domain=lambda self: [('groups_id', 'in', self.env.ref('embassy_letter.embassy_letter_approve_group').id)])

    state = fields.Selection([
        ('wfa', "Waiting For Approve"),
        ('hr', "HR Department"),
        ('rejected', "Rejected"),
        ('done', "Done")
    ], default='wfa', string="Stage", track_visibility='onchange')

    def hr_department(self):
        self.state = 'hr'

    def reject(self, **additional_values):
        template = self.env.ref('embassy_letter.mail_template_reject_embassy_letter')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        return self.write({'state': 'rejected',
                           'reject_reason': additional_values.get('reject_reason'),
                           })

    # @api.multi
    def done(self):
        template = self.env.ref('embassy_letter.mail_template_done_embassy_letter')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'done'

    @api.model
    def get_email_to(self):
        user = self.env['res.users'].search([('groups_id', '=', self.env.ref('embassy_letter.embassy_letter_approve_group').id)])
        user_group = self.env.ref("embassy_letter.embassy_letter_approve_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('embassy.letter') or '/'
            vals['name'] = seq

        res = super(EmbassyLetter, self).create(vals)
        # user = self.env['res.users'].search([('groups_id', '=', self.env.ref('embassy_letter.embassy_letter_approve_group').id)])
        # vals['hr_man'] = user
        # # print(hr_man)
        template = self.env.ref('embassy_letter.mail_template_wfa_embassy_letter')
        self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res


class VisaType(models.Model):
    _name = 'visa.type'

    name = fields.Char(string='Name', index=True, required=True)


class TravelNature(models.Model):
    _name = 'travel.nature'

    name = fields.Char(string='Name', index=True, required=True)


class RejectMessage(models.TransientModel):
    _name = 'reject.message.embassy'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        embassy_letter = self.env['embassy.letter'].browse(self.env.context.get('active_ids'))
        return embassy_letter.reject(reject_reason=self.reject_reason)


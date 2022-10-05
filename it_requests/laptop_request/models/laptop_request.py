# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_


class LaptopRequest(models.Model):
    _name = 'laptop.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string="Employee", track_visibility='always', readonly=True,
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    # employee_device_id = fields.Char(string="Biometric Device ID", related='employee_name.device_id')
    create_date = fields.Date(string='Created On', default=fields.Date.today(), readonly=True)
    reject_reason = fields.Text(string='Reject Reason')

    state = fields.Selection([
        ('wfa', "Waiting For Approve"),
        ('hr', "HR Department"),
        ('rejected', "Rejected"),
        ('done', "Done")
    ], default='wfa', string="Stage", track_visibility='onchange')

    def hr_department(self):
        self.state = 'hr'

    def reject(self, **additional_values):
        template = self.env.ref('laptop_request.mail_template_reject_access_card')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

        return self.write({'state': 'rejected',
                           'reject_reason': additional_values.get('reject_reason')})

    def done(self):
        template = self.env.ref('laptop_request.mail_template_done_access_card')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'done'

    @api.model
    def get_email_to(self):
        user_group = self.env.ref("laptop_request.access_card_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('replace.access.card') or '/'
            vals['name'] = seq
        res = super(LaptopRequest, self).create(vals)
        template = self.env.ref('laptop_request.mail_template_access_card')
        self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)

        return res


class RejectMessageLaptopRequest(models.TransientModel):
    _name = 'reject.message.laptop.request'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        access_card = self.env['replace.access.card'].browse(self.env.context.get('active_ids'))
        return access_card.reject(reject_reason=self.reject_reason)


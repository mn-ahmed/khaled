# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_


class SimCardRequest(models.Model):
    _name = 'sim.card'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string="Employee", track_visibility='always', readonly=True,
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    department_name = fields.Many2one('hr.department', related='employee_name.department_id')
    manager_name = fields.Many2one('hr.employee', related='employee_name.parent_id')
    employment_type = fields.Many2one('employment.type', related='employee_name.employment_type')

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
        template = self.env.ref('ess_requests.mail_template_reject_sim_card')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

        return self.write({'state': 'rejected',
                           'reject_reason': additional_values.get('reject_reason')})

    def done(self):
        template = self.env.ref('ess_requests.mail_template_done_sim_card')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'done'

    @api.model
    def get_email_to(self):
        user_group = self.env.ref("ess_requests.sim_card_request_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('sim.card') or '/'
            vals['name'] = seq
        res = super(SimCardRequest, self).create(vals)
        template = self.env.ref('ess_requests.mail_template_sim_card_request')
        self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res


class RejectMessageSIM(models.TransientModel):
    _name = 'reject.message.sim.card'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        sim_card = self.env['sim.card'].browse(self.env.context.get('active_ids'))
        return sim_card.reject(reject_reason=self.reject_reason)


# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_


class VMRequest(models.Model):
    _name = 'vm.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string="Employee", track_visibility='onchange', readonly=True,
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    direct_manager = fields.Many2one('hr.employee', related='employee_name.parent_id')
    vm_name = fields.Char(string='VM Project Name', required=True, placeholder="The name of the project used in VM ")
    ram = fields.Char(string='RAM', required=True, track_visibility='onchange')
    cpu = fields.Char(string='CPU', required=True, track_visibility='onchange')
    hard_disk = fields.Char(string='HD', required=True, track_visibility='onchange')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    create_date = fields.Date(string='Created On', default=fields.Date.today(), readonly=True)
    reject_reason = fields.Text(string='Reject Reason')

    vm_ip = fields.Char(string='IP', track_visibility='onchange')
    vm_username = fields.Char(string='User Name', track_visibility='onchange')
    vm_password = fields.Char(string='Password', track_visibility='onchange')

    os_requested = fields.Selection([
        ('win10', "WIN 10"),
        ('win_ser12', "WIN Server 12"),
        ('win_ser16', "WIN Server 16"),
        ('win_ser19', "WIN Server 19"),
        ('linux_red', "Linux Red Hat"),
        ('linux_ubu', "Linux Ubuntu"),
        ('linux_cent', "Linux Centos"),
    ],  string="OS", track_visibility='onchange')

    default_software = fields.Many2many('default.software', string="Default software on VM", track_visibility='onchange')
    needed_software = fields.Text(string='Other Software needed')
    version = fields.Char(string='Version', )

    state = fields.Selection([
        ('new', "New"),
        ('wfa', "Waiting For Approve"),
        ('manager_approve', "Manager Approve"),
        ('it', "IT Department"),
        ('rejected', "Rejected"),
        ('done', "Done")
    ], default='new', string="Stage", track_visibility='onchange')

    def wfa_submit(self):
        template1 = self.env.ref('it_requests.mail_template_vm_request_employee_mail')
        self.env['mail.template'].browse(template1.id).send_mail(self.id, force_send=True, raise_exception=True)
        template = self.env.ref('it_requests.mail_template_request_vm')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'wfa'

    def manager_approve(self):
        template = self.env.ref('it_requests.mail_template_request_vm_approved')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'manager_approve'

    def it_approve(self):
        self.state = 'it'

    def reject(self, **additional_values):
        template = self.env.ref('it_requests.mail_template_reject_access_card')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

        return self.write({'state': 'rejected',
                           'reject_reason': additional_values.get('reject_reason')})

    def done(self):
        template = self.env.ref('it_requests.mail_template_vm_request_done')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        self.state = 'done'

    @api.model
    def get_email_to(self):
        user_group = self.env.ref("it_requests.it_request_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def get_approve_email_to(self):
        user_group = self.env.ref("it_requests.it_request_manager_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('vm.request') or '/'
            vals['name'] = seq
        res = super(VMRequest, self).create(vals)
        # template = self.env.ref('it_request.mail_template_access_card')
        # self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res


class RejectMessageVMRequest(models.TransientModel):
    _name = 'reject.message.vm.request'

    reject_reason = fields.Text('Reject Reason')

    def action_reject_reason(self):
        vm_request = self.env['vm.request'].browse(self.env.context.get('active_ids'))
        return vm_request.reject(reject_reason=self.reject_reason)


class VMRequestSoftware(models.TransientModel):
    _name = 'default.software'

    name = fields.Char('Name')


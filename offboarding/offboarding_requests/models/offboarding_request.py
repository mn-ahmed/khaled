from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, Warning



class OffBoarding(models.Model):
    _name = 'offboarding.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']

    name = fields.Char(string='Req.No', copy=False, readonly=True, index=True, default=lambda self: _('New'),
                       required=True, track_visibility='always')
    employee_name = fields.Many2one('hr.employee', string="Employee", track_visibility='always', readonly=True,
                                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)]
                                                                                        , limit=1))
    employee_full_name = fields.Char(string="Employee Full Name", related='employee_name.employee_full_name')
    employee_direct_manager = fields.Many2one('hr.employee', string="Direct Manager", related='employee_name.parent_id')
    employee_project_manager = fields.Many2one('hr.employee', string="Project Manager", related='employee_name.employee_project_manager')
    employee_project = fields.Many2many('employee.project', string="Project", related='employee_name.employee_project')
    employee_email = fields.Char(string="Email", related='employee_name.work_email')
    bbi_last_date = fields.Date(string='Final Last day In BBI', track_visibility='onchange')
    vacations_balance = fields.Char(string="Vacations Balance")
    # onboarding_request = fields.Many2one('onboarding.proccess', default=lambda self: self.env['onboarding.proccess'].search([
    #     ('employee_id', '=', self.employee_name)], limit=1))
    employee_laptop = fields.Many2one('product.template', readonly=True, compute='get_employee_laptop')
    #,default=lambda self: self.env['product.template'].search([('employee_device', '=', self.employee_name)], limit=1)
    hr_dep = fields.Boolean(string='HR Department')
    medical_card = fields.Boolean(string='Medical Card', track_visibility='always')
    sim_card = fields.Boolean(string='SIM Card', track_visibility='always')
    access_card = fields.Boolean(string='Access Card', track_visibility='always')
    uniform = fields.Boolean(string='Uniform or not taken in the first place', track_visibility='always')
    Company_key = fields.Boolean(string='Company key or not taken in the first place', track_visibility='always')

    it_dep = fields.Boolean(string='IT Department')
    laptop_handover = fields.Boolean(string='Handed over the Laptop', track_visibility='always')
    email_handover = fields.Boolean(string='Email Address is no longer functional and now available', track_visibility='always')

    finance_dep = fields.Boolean(string='Finance Department')
    no_loan = fields.Boolean(string='No Loans', track_visibility='always')
    signed_resignations = fields.Boolean(string='Signed the resignations document', track_visibility='always')
    fully_paid = fields.Boolean(string='The employee is fully paid', track_visibility='always')

    erp_dep = fields.Boolean(string='ERP Department')
    user_deactivated = fields.Boolean(string='User is now deactivated', track_visibility='always')

    state = fields.Selection([
        ('hr', "HR"),
        ('it', "IT"),
        ('finance', "Finance"),
        ('erp', "ERP"),
        ('done', "Done"),
    ], default='hr', string="Stage", track_visibility='onchange')

    def get_employee_laptop(self):
        for rec in self:
            onboarding_request_lap = self.env['onboarding.proccess'].search([('employee_id.id', '=', rec.employee_name.id)])
            rec.employee_laptop = onboarding_request_lap.laptop

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('offboarding.request') or '/'
            vals['name'] = seq
        res = super(OffBoarding, self).create(vals)
        template = self.env.ref('offboarding.mail_template_offboarding_creation_mail')
        # self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        return res

    def hr_approve(self):
        if self.env.user == self.employee_name.user_id:
            # raise ValidationError("Please, You Can't Approve Your request ")
            self.state = 'it'
        else:
            template = self.env.ref('offboarding.mail_template_offboarding_hr_request_mail')
            # self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
            self.state = 'it'

    def it_approve(self):
        if self.env.user == self.employee_name.user_id:
        #     raise ValidationError("Please, You Can't Approve Your request ")
        # else:
            empolyee_onboarding_request = self.env['onboarding.proccess'].search([('employee_id.id', '=', self.employee_name.id)],
                                                                        limit=1)
            empolyee_onboarding_request.onboarding_offboarding = True
            self.write({'state': 'finance',
                       'employee_laptop.state': 'available',
                        })
            # self.onboarding_request.laptop = False
            template = self.env.ref('offboarding.mail_template_offboarding_it_request_mail')
            # self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

    def finance_approve(self):
        if self.env.user == self.employee_name.user_id:
            raise ValidationError("Please, You Can't Approve Your request ")
        else:
            self.state = 'erp'
            template = self.env.ref('offboarding.mail_template_offboarding_finance_request_mail')
            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)

    def erp_approve(self):
        if self.env.user == self.employee_name.user_id:
            raise ValidationError("Please, You Can't Approve Your request ")
        else:
            self.state = 'done'
            template = self.env.ref('offboarding.mail_template_offboarding_erp_request_mail')
            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)


    @api.model
    def get_email_to_hr(self):
        user_group = self.env.ref("offboarding.offboarding_request_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def get_email_to_it(self):
        user_group = self.env.ref("offboarding.offboarding_request_it_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def get_email_to_finance(self):
        user_group = self.env.ref("offboarding.offboarding_request_finance_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def get_email_to_erp(self):
        user_group = self.env.ref("offboarding.offboarding_request_erp_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)
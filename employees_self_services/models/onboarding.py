from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime,date


class OnBoardingPorcess(models.Model):
    _name = 'onboarding.proccess'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string="Employee", track_visibility='always', required=True)
    email = fields.Char("Email", index=True, required=True, track_visibility='onchange')
    laptop = fields.Many2one("product.template", string='Laptop Model', track_visibility='onchange',
                             domain=[("type", '=', 'product'), ("state", '=', 'available')])
    # model_number = fields.Char("Model Number", required=True, track_visibility='onchange')
    sim_card = fields.Char("Sim Card No", track_visibility='onchange')
    title = fields.Many2one("hr.job", string="Job Title", track_visibility='onchange', required=True)
    date = fields.Date(default=fields.Date.today, index=True, string='Date', track_visibility='onchange')
    company_id_no = fields.Char(string='Company ID Number', track_visibility='onchange')
    user_id = fields.Many2many('res.users', compute='compute_user_on', store=True)
    upload_file = fields.Binary(string="Upload File")
    description = fields.Text('Description')
    hr_tasks_completed = fields.Boolean(string='HR Tasks Completed')
    welcome_email = fields.Boolean(string='Welcome Email', track_visibility='always')
    handbook = fields.Boolean(string='Handbook', track_visibility='always')
    contact_assignment = fields.Boolean(string='Contact Assignment', track_visibility='always')
    hiring_documents = fields.Boolean(string='Hiring Documents', track_visibility='always')
    medical_insurance = fields.Boolean(string='Medical Insurance', track_visibility='always')
    social_insurance = fields.Boolean(string='Social Insurance', track_visibility='always')
    onboarding_offboarding = fields.Boolean(string='onboarding offboarding', default=False)
    lap_needed = fields.Boolean(string='No Laptop Needed', track_visibility='onchange')
    lap_deadline = fields.Date(string='Laptop Delivery Deadline', track_visibility='onchange')
    gender = fields.Selection([
        ('male', "Male"),
        ('female', "Female")
    ], string="Gender", track_visibility='onchange')
    id_type = fields.Selection([
        ('trainee', "Trainee"),
        ('employee', "Employee"),
        ('part', "Part Time"),
        ('international', "BBI International")
    ], string="ID Type", track_visibility='onchange')
    start_date = fields.Date(string='Start Date')
    leave_opening_balance = fields.Char(string='Leave Opening Balance', compute='compute_leave_balance')
    state = fields.Selection([
        ('a', "IT Lead"),
        ('m', "Direct Manager"),
        ('b', "ERP Admin"),
        ('c', "Finance"),
        ('e', "HR Admin"),
        ('f', "Done")
    ], default='a', string="Stage", track_visibility='onchange')
    # ('d', "Marketing"),

    @api.onchange('id_type')
    def company_number_sequence(self):
        for rec in self:
            if rec.id_type:
                if rec.id_type == 'trainee':
                    seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.trainee')
                    print(seq)
                    # rec.company_id_no = seq
                elif rec.id_type == 'employee':
                    seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.employee')
                    # rec.company_id_no = seq
                elif rec.id_type == 'part':
                    seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.part.time')
                    # rec.company_id_no = seq
                elif rec.id_type == 'international':
                    seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.international')
                print(seq)

                 # rec.company_id_no = seq
                print(seq)
                return rec.update({'company_id_no': seq})

        # if self.company_id_no:
        #     existing_company_no = self.env['onboarding.proccess'].search([('id', '!=', self.id)
        #                                                                    ,('company_id_no', '=', self.company_id_no)])
        #     if existing_company_no:
        #         raise Warning("You Can not have the same Company Number in Onboarding twiceee")

    @api.depends('start_date')
    def compute_leave_balance(self):
        for rec in self:
            if rec.start_date:
                # today = fields.Datetime.now()
                # months = (today.year - rec.start_date.year)*12 + today.month - rec.start_date.month

                months = 12 - rec.start_date.month
                print(months, 'monthsssss')
                rec.leave_opening_balance = (months+1)*1.75
            else:
                rec.leave_opening_balance = 0

    @api.model
    def get_email_to_hr(self):
        user_group = self.env.ref("offboarding.resignation_request_hr_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.depends('state')
    def compute_user_on(self):
        for rec in self:
            if rec.state == 'a':
                user_group = self.env.ref('employees_self_services.onboarding_cycle_it_lead')
                email_list = [
                    usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
                return ",".join(email_list)

                # flag = self.env['res.users'].search(
                #     [('groups_id', '=', rec.env.ref('employees_self_services.onboarding_cycle_it_lead').id)])
                # if flag:
                #     rec.user_id = flag
            if rec.state == 'b':
                user_group = self.env.ref('employees_self_services.onboarding_cycle_erp_admin')
                email_list = [
                    usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
                return ",".join(email_list)
                # flag = self.env['res.users'].search(
                #     [('groups_id', '=', rec.env.ref('employees_self_services.onboarding_cycle_erp_admin').id)])
                # if flag:
                #     rec.user_id = flag
            if rec.state == 'c':
                user_group = self.env.ref('employees_self_services.onboarding_cycle_finance')
                email_list = [
                    usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
                return ",".join(email_list)

                # flag = self.env['res.users'].search(
                #     [('groups_id', '=', rec.env.ref('employees_self_services.onboarding_cycle_finance').id)])
                # if flag:
                #     rec.user_id = flag
            if rec.state == 'm':
                user_group = self.env.ref('employees_self_services.onboarding_cycle_direct_manager')
                email_list = [
                    usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
                return ",".join(email_list)

                # flag = self.env['res.users'].search(
                #     [('groups_id', '=', rec.env.ref('employees_self_services.onboarding_cycle_direct_manager').id)])
                # if flag:
                #     rec.user_id = flag
            if rec.state == 'e':
                user_group = self.env.ref('employees_self_services.onboarding_cycle_hr_admin')
                email_list = [
                    usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
                return ",".join(email_list)

                # flag = self.env['res.users'].search(
                #     [('groups_id', '=', rec.env.ref('employees_self_services.onboarding_cycle_hr_admin').id)])
                # if flag:
                #     rec.user_id = flag

    def pass_to_erp_admin(self):
        flag = self.env['res.users'].has_group('employees_self_services.onboarding_cycle_direct_manager')
        if flag and (self.state == 'm'):

            self.state = 'b'
            template = self.env.ref('employees_self_services.mail_template_onboarding_process_for_erp_admin')

            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        else:
            raise ValidationError("You don't have a permission of direct manager to pass to the next step ")

    ##################
    def pass_to_finance(self):
        flag = self.env['res.users'].has_group('employees_self_services.onboarding_cycle_erp_admin')
        if flag and (self.state == 'b'):
            self.state = 'c'
            template = self.env.ref('employees_self_services.mail_template_onboarding_process_for_finance')

            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        else:
            raise ValidationError("You don't have a permission of erp admin to pass to the next step ")

    ############################
    def pass_to_d_manager(self):
        flag = self.env['res.users'].has_group('employees_self_services.onboarding_cycle_it_lead')
        if flag and (self.state == 'a'):
            self.state = 'm'
            template = self.env.ref('employees_self_services.mail_template_onboarding_process_for_manager')

            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        else:
            raise ValidationError("You don't have a permission of it lead to pass to the next step ")

    def pass_to_hr_admin(self):
        flag = self.env['res.users'].has_group('employees_self_services.onboarding_cycle_finance')
        if flag and (self.state == 'c'):
            self.state = 'e'
            template = self.env.ref('employees_self_services.mail_template_onboarding_process_for_hr_admin')

            self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True, raise_exception=True)
        else:
            raise ValidationError("You don't have a permission of finance to pass to the next step ")

    def pass_to_done(self):
        flag = self.env['res.users'].has_group('employees_self_services.onboarding_cycle_hr_admin')
        if flag and (self.state == 'e'):
            self.state = 'f'
        else:
            raise ValidationError("You don't have a permission of hr admin to pass to the next step ")

    ##################################################################################################################
    # @api.multi
    # def write(self, vals):
    #     res = super(OnBoardingPorcess, self).write(vals)
    #     self.company_number_sequence()
    #     if vals.get('id_type'):
    #         if vals.get('id_type') == 'trainee':
    #             seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.trainee')
    #             print(seq)
    #             # rec.company_id_no = seq
    #         elif vals.get('id_type') == 'employee':
    #             seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.employee')
    #             # rec.company_id_no = seq
    #         elif vals.get('id_type') == 'part':
    #             seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.part.time')
    #             # rec.company_id_no = seq
    #         elif vals.get('id_type') == 'international':
    #             seq = self.env['ir.sequence'].next_by_code('onboarding.proccess.international')
    #         print(seq)
    #
    #         self.company_id_no = seq
    #         print(seq)
    #         # self.update({'company_id_no': seq})
    #
    #     # if vals.get('company_id_no'):
    #     #     existing_company_no = self.env['onboarding.proccess'].search(
    #     #         [('employee_id', '!=', vals.get('employee_id')), ('company_id_no', '=', vals.get('company_id_no'))])
    #     #     if existing_company_no:
    #     #         raise ValidationError("You Can not have the same Company ID Number")
    #
    #     return res

    @api.model
    def create(self, vals):
        res = super(OnBoardingPorcess, self).create(vals)
        if vals.get('laptop'):
            laptops = self.env['product.template'].browse([vals['laptop']])
            laptops.state = 'preparing'
        # if vals.get('company_id_no'):
        #     existing_company_no = self.env['onboarding.proccess'].search([('employee_id', '!=', vals.get('employee_id')),('company_id_no', '=',  vals.get('company_id_no'))])
        #     if existing_company_no:
        #         raise ValidationError("You Can not have the same Company ID Number")
        self.company_number_sequence()
        template = self.env.ref('employees_self_services.mail_template_onboarding_process')
        self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True, raise_exception=True)
        return res

    def laptop_delivered(self):
        flag = self.env['res.users'].has_group('employees_self_services.onboarding_cycle_it_lead')
        if flag and self.laptop:
            self.laptop.state = 'used'
            self.onboarding_offboarding = False
        else:
            if not flag:
                raise ValidationError("You don't have a permission")
            elif not self.laptop:
                raise ValidationError("Please select laptop!")



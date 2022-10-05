
##################################################################################
from odoo import models, fields, api
from odoo.exceptions import Warning, _logger
from datetime import datetime, date


class EmployeeTravelReqest(models.Model):
    _name = 'hr.emp.travel.request'
    _description = "Travel Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #@api.multi
    def hr_manager_user_ids_get(self):
        self.ensure_one()
        hr_group_ids = self.env.ref('hr.group_hr_manager').users.ids
        self.hr_manager_user_ids = [(6, 0, hr_group_ids)]

    user_id = fields.Many2one('res.users')
    hr_manager_user_ids = fields.Many2many('res.users', compute="hr_manager_user_ids_get")

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    # related fields
    department_id = fields.Many2one(related="employee_id.department_id", store=True)
    company_id = fields.Many2one(related="employee_id.company_id", store=True)
    parent_id = fields.Many2one(related="employee_id.parent_id", store=True)
    job_id = fields.Many2one(related="employee_id.job_id", store=True)
    grade_id = fields.Many2one(related="employee_id.grade_id", store=True)
    currency_id = fields.Many2one(related="employee_id.company_id.currency_id", store=True)
    # Travel Dates
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    expect_travel_days = fields.Integer(string="Days", compute="compute_days")
    state = fields.Selection(
        [('draft', 'Draft'), ('waiting', 'Waiting for confirmation'), ('confirmed', 'Confirmed'), ('approved', 'Approved'), ('ongoing', 'Ongoing'),
         ('trip_completed', 'Trip Completed'), ('closed', 'Closed'), ('rejected', 'Rejected'), ('canceled', 'Canceled')], default="draft", track_visibility="onchange")
    # travel locations
    travel_location_ids = fields.One2many('hr.emp.travel.location', 'travel_request_id_ref', required=True)
    total_travel_days = fields.Integer(string="Days", compute="compute_days_travel_location")
    # Expenses(proposed/actual)
    expense_amount_ids = fields.One2many('hr.expense.amount', 'travel_request_id')
    total_expense_amount = fields.Monetary(string="Grand Total", compute="compute_total_expense_amount", store=False)
    ticket_book = fields.Boolean(string="Company Books ticket for You", track_visibility="onchange")
    # Log
    request_by = fields.Many2one('res.users', default=lambda self: self.env.uid)
    approved_by = fields.Many2one('res.users')
    rejected_by = fields.Many2one('res.users')
    request_date = fields.Date(string="Requested Date", default=date.today())
    approved_date = fields.Date()
    rejected_date = fields.Date()
    reject_reason = fields.Char("Reason For Reject")
    # Reason
    reason = fields.Text(string="Reason")
    # Currency
    currency_ids = fields.One2many('hr.travel.currency', 'travel_request_id')
    # Expenses
    expenses_ids = fields.One2many('hr.expense', 'travel_request_id_ref')

    @api.model
    def create(self, vals):
        travel_request = super(EmployeeTravelReqest, self).create(vals)
        travel_request.sudo().name = self.env['ir.sequence'].next_by_code('emp.travel.request.id')
        return travel_request

    @api.model
    def default_get(self, fields_list):
        employee_default = super(EmployeeTravelReqest, self).default_get(fields_list)
        employee_default.update({
            'employee_id': self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id
        })
        return employee_default

    # Date validation
    @api.onchange('from_date')
    def check_from_dates(self):
        if self.from_date:
            if self.from_date < date.today():
                raise Warning("Please enter  valid date greater than today("+str(date.today())+")")
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise Warning("Please Enter Valid Dates")

    @api.onchange('to_date')
    def check_to_dates(self):
        if self.to_date:
            if self.to_date < date.today():
                raise Warning("Please enter valid date greater than today(" + str(date.today()) + ")")

        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise Warning("Please Enter Valid Dates")

    # grade and expenses values
    @api.onchange('employee_id', 'expect_travel_days')
    def fill_by_grade(self):
        if self.grade_id:
            expense_ids = self.env['hr.emp.grade.config'].sudo().search([('grade_id', '=', self.grade_id.id)], limit=1)
            if expense_ids.expense_line_ids:
                list_ids = []
                for each in expense_ids.expense_line_ids:
                    temp = {}
                    temp['travel_request_id'] = self.id
                    temp['expense_id'] = each.expense_id.id
                    temp['currency_id'] = each.currency_id.id
                    temp['exp_type'] = each.exp_type
                    temp['product_id'] = each.product_id.id
                    if each.exp_type == 'daily':
                        if self.expect_travel_days > 1:
                            temp['total'] = each.amount * self.expect_travel_days
                        else:
                            temp['total'] = each.amount
                    else:
                        temp['total'] = each.amount
                    temp['amount'] = each.amount
                    temp['approved_amount'] = each.amount

                    object = self.env['hr.expense.amount'].sudo().create(temp)
                    list_ids.append(object.id)
                self.expense_amount_ids = self.env['hr.expense.amount'].sudo().browse(list_ids)
            else:
                self.expense_amount_ids = None
                raise Warning("Please Set the Grade Expenses in the  Configuration=>Expenses(Grade) Menu !!!")
        else:
            self.expense_amount_ids = None
            raise Warning("Please Set the Grade in the Employee Details!!!")
        if self.employee_id.parent_id.user_id:
            self.user_id = self.employee_id.parent_id.sudo().user_id.id

    # Calculate save at (expect_travel_days) the difference between dates
    @api.depends('from_date', 'to_date')
    def compute_days(self):
        for each in self:
            if each.from_date and each.to_date:
                d1 = datetime.strptime(str(each.to_date), '%Y-%m-%d')
                d2 = datetime.strptime(str(each.from_date), '%Y-%m-%d')
                daysDiff = (d1 - d2).days
                each.expect_travel_days = int(daysDiff) + 1

    # Calculate the days(total_travel_days) from different locations
    @api.depends('travel_location_ids')
    def compute_days_travel_location(self):
        for each in self:
            if each.travel_location_ids:
                each.total_travel_days = sum([i.travel_days for i in each.travel_location_ids])

    # amount calculate
    @api.depends('expense_amount_ids.total', 'expense_amount_ids.approved_amount')
    def compute_total_expense_amount(self):
        for each in self:
            if each.expense_amount_ids:
                each.total_expense_amount = sum([i.total for i in each.expense_amount_ids])

    # constraints
    @api.constrains('travel_location_ids')
    def check_locations(self):
        self.ensure_one()
        if self.travel_location_ids:
            return
        else:
            raise Warning("Please insert locations")

    #@api.multi
    @api.constrains('to_date', 'from_date')
    def check_date(self):
        self.ensure_one()
        if self.from_date < date.today():
            raise Warning("Please Enter Future Dates Past dates not allowed")
        if self.from_date and self.to_date:
            if self.to_date < self.from_date:
                raise Warning("Please Enter Valid Dates")
        check_record_from_dates = self.env['hr.emp.travel.request'].search(
            [('employee_id', '=', self.employee_id.id),
             ('from_date', '<=', self.from_date),
             ('to_date', '>=', self.from_date),
             ('id', '!=', self.id),
             ('state', 'not in', ['canceled', 'rejected'])])
        check_record_to_dates = self.env['hr.emp.travel.request'].search(
            [('employee_id', '=', self.employee_id.id),
             ('from_date', '<=', self.to_date),
             ('to_date', '>=', self.to_date),
             ('id', '!=', self.id),
             ('state', 'not in', ['canceled', 'rejected'])])
        check_records = self.env['hr.emp.travel.request'].search(
            [('from_date', '>=', self.from_date),
             ('to_date', '<=', self.to_date),
             ('employee_id', '=', self.employee_id.id),
             ('id', '!=', self.id),
             ('state', 'not in', ['canceled', 'rejected'])])
        for locations in self.travel_location_ids:
            locations.check_date()
        if check_records or check_record_from_dates or check_record_to_dates:
            raise Warning("Already booked in " + str(self.from_date) + " to "+str(self.to_date)+"\n Select different dates")

    @api.constrains('expect_travel_days', 'total_travel_days')
    def check_days(self):
        self.ensure_one()
        if self.expect_travel_days < self.total_travel_days:
            raise Warning(
                "Please check your travel days in 'Travel information' tab it must be less or equal to the Outer days")

    # send manager button
    def action_send_manager(self):
        mail_address = self.parent_id.work_email
        if not self.travel_location_ids:
            raise Warning("Please enter the travel information before submit to manager")
        if mail_address:
            try:
                template_id = self.env['ir.model.data'].get_object_reference('flexi_hr',
                                                                             'send_to_manager_request_template')
                if template_id:
                    template_obj = self.env['mail.template'].browse(template_id[1])
                    template_obj.send_mail(self.id, force_send=True, raise_exception=False)
            except Exception:
                _logger.info('Mail Server not Cofigured', exc_info=True)
        self.state = 'waiting'
        if self.employee_id.parent_id.user_id:
            self.user_id = self.employee_id.parent_id.sudo().user_id.id

    # confirm button
    def action_confirm(self):
        self.check_days()
        admin1 = self.env.ref('base.group_erp_manager')
        if self.env.uid in admin1.users.ids:
            if not self.travel_location_ids:
                raise Warning("Without place no request get Proceed.")
            self.sudo().state = 'confirmed'
        elif self.env.uid != self.employee_id.user_id.id:
            if not self.travel_location_ids:
                raise Warning("Without place request not proceed.")
            self.sudo().state = 'confirmed'
        else:
            raise Warning("You are not allow to confirm this request,\nplease contact to the administrator.")

    # approve button
    def action_approve(self):
        self.check_days()
        hr_user = self.env.ref('hr.group_hr_manager')
        admin1 = self.env.ref('base.group_erp_manager')
        if (self.env.uid in hr_user.users.ids) or (self.env.uid in admin1.users.ids):
            if not self.travel_location_ids:
                raise Warning("Without place request not proceed.")
        else:
            raise Warning("You are not allow to approve trip,\n please contact to the administrator.")
        for currency_exp in self.currency_ids:
            if not currency_exp.account_id:
                raise Warning("Please check currency tab \nAccount is missing.")
            if not currency_exp.status:
                raise Warning("Please check currency tab \nJournal entry remaining.")
        self.state = 'approved'
        self.approved_by = self.env.uid
        self.approved_date = date.today()
        self.send_travel_request_email()


    # ongoing button
    def action_ongoing(self):
        if not self.travel_location_ids:
            raise Warning("Without place request not proceed.")
        self.state = 'ongoing'

    #  trip complete button
    def complete_trip(self):
        for currency_exp in self.currency_ids:
            if not currency_exp.account_id:
                raise Warning("Please check currency tab \nAccount is missing.")
        if not self.travel_location_ids:
            raise Warning("Without place request not proceed.")
        self.sudo().state = 'trip_completed'

    # Close button
    def action_close(self):
        for check in self.expenses_ids:
            if not (check.state in ['done', 'refused']):
                raise Warning("Verify expenses payment is remaining.")
        for proposed_exp in self.expense_amount_ids:
            if not proposed_exp.status:
                raise Warning("Please complete all proposed expenses.")
        for currency_exp in self.currency_ids:
            if not currency_exp.status:
                raise Warning("Please complete the payment of other currency.")
        self.sudo().state = 'closed'

    # cancel button
    def action_cancel(self):
        self.sudo().state = 'canceled'

    # reject button
    def action_reject(self):
        view_id = self.env.ref("flexi_hr.aspl_reason_reject_wizard")
        return {
            'name': 'Hr Travel Request Reject Reason',
            'res_model': 'hr.travel.request.reject',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_travel_request_id': self.id}
        }

    #  reset button
    def action_reset(self):
        self.state = 'draft'

    #  mail Sending
    #@api.multi
    def send_travel_request_email(self):
        try:
            template_id = self.env['ir.model.data'].get_object_reference('flexi_hr',
                                                                         'draft_employee_request_template')
            if template_id:
                template_obj = self.env['mail.template'].browse(template_id[1])
                template_obj.send_mail(self.id, force_send=True, raise_exception=False)
        except Exception:
            _logger.info('Mail server not cofigured', exc_info=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
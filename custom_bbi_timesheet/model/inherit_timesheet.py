from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import AccessError
from datetime import date

class LagortaUpdateProject(models.Model):
    _inherit = "project.project"

    one_approve = fields.Boolean(default=True, string="One Cycle Approve")

    two_approve = fields.Boolean(string="Two Cycle Approve")


class CheckEmployee(models.Model):
    _inherit = 'hr.employee'

    reject_validation = fields.Boolean(string="reject validation", default=False, groups="hr.group_hr_user")
    timesheet_validate_manager = fields.Many2one('hr.employee', "Validate timesheet", groups="hr.group_hr_user")


class InheritTimesheetWorkFlow(models.Model):
    _name = "account.analytic.line"
    _inherit = ["account.analytic.line", 'mail.thread']

    is_request = fields.Boolean(default=False)
    is_leave = fields.Boolean(default=False)
    one_approve_tm = fields.Boolean(string="One Cycle Approve", compute="compute_on_cycle")
    two_approve_tm = fields.Boolean(string="Two Cycle Approve", compute="compute_on_cycle")
    user_id = fields.Many2one('res.users', string='User', track_visibility='onchange',
                              default=lambda self: self.env.user)
    # validated_statu = fields.Selection(selection_add=[('course', 'Course')])
    validated_statu = fields.Selection([('draft', "Draft"), ('submit', "Submit"), ('approved', "Approved"),
                                         ('validated', "Validated"),
                                        ('rejected', "Rejected")], default='draft', string="Stage", track_visibility='onchange')

    reject_reason = fields.Text(string="Reject Reason")
    reject_validation = fields.Boolean(string="reject validation", default=False)
    validate_user_id = fields.Many2one(related='employee_id.timesheet_validate_manager.user_id')



    def copy(self, default=None):
        record = super(InheritTimesheetWorkFlow, self).copy(default=default)

        if record.validated_statu:
            record.validated_statu = 'draft'
            # print("ssssss")

        return record

    def compute_on_cycle(self):
        for rec in self:
            if rec.project_id.two_approve or rec.project_id.one_approve:
                if rec.project_id.two_approve or (rec.project_id.one_approve and rec.project_id.two_approve):
                    rec.two_approve_tm = True
                    rec.one_approve_tm = False
                    return
                elif rec.project_id.one_approve and not rec.project_id.two_approve:
                    rec.one_approve_tm = True
                    rec.two_approve_tm = False

            return

    @api.model
    def create(self, value):
        total = []
        result = []
        total_planned = []
        res = super(InheritTimesheetWorkFlow, self).create(value)
        task_check = res.mapped('task_id')
        planned = task_check.planned_hours
        date_tocheck = res.mapped('date')
        employee_check = res.mapped('employee_id')

        if value.get('product_id', True):

              ##### weekends and leaves #########

            records = self.env['hr.employee.public'].search([('name', '=', res['employee_id'].name)])
            for record in records:
                for item in record.resource_calendar_id:
                    for order in item.attendance_ids:
                        result.append(dict(order._fields['dayofweek'].selection).get(order.dayofweek))
                    # for line in item.global_leave_ids:
                    #     if (res['date'] >= line.date_from.date()) and (res['date'] <= line.date_to.date()):
                    #         raise ValidationError("Warning : You Can't Make Timesheet, You need an Approve .")
            if res['is_request'] == False and res['is_timesheet']:
                if (res['date'].strftime("%A") not in result):
                    raise ValidationError("Warning : this is weekend, please you need an approve.")

              ##### time cont be zero or more than 8 hours #########


            recordset = self.search([('date', '=', date_tocheck[0]), ('employee_id.name', '=', employee_check.name)])
            for record in recordset:
                if res['is_request'] == False and res['is_timesheet'] == False:
                    total.append(record.unit_amount)

            recordprojects = self.search([('task_id', '=', task_check.id), ('employee_id.name', '=', employee_check.name)])
            for record in recordprojects:
                total_planned.append(record.unit_amount)
            # if res['is_request'] == False and res['is_leave'] == False:
            #     if sum(total) > 8:
            #         raise ValidationError("Warning : You can't submit more than 8 hours per Day")

            if task_check.id and planned != 0:
                if sum(total_planned) > planned:
                    raise ValidationError("Warning: You can't submit more planned hours for this Task")

            if 'unit_amount' in value:
              if res['unit_amount'] <= 0:
                  raise ValidationError("Your time spent Can't be zero ")

            all_objs = self.env['account.analytic.line'].search([('validated_statu', '=', 'rejected')])
            if all_objs:
                for obj in all_objs:
                    for emp in obj.employee_id:
                        emp.sudo().write({
                            'reject_validation': True
                        })
                # if res.employee_id.reject_validation == True and res.is_leave == False:
                #     raise ValidationError("You cannot add timesheet line while you have rejected one")

        return res

    # def write(self, value):
    #
    #     res = super(InheritTimesheetWorkFlow, self).write(value)
    #     result = []
    #     total = []
    #     ess_total = []
    #     total_planned = []
    #     task_check = self.mapped('task_id')
    #     planned = task_check[0].planned_hours
    #     date_tocheck = self.mapped('date')
    #     # employee_check = self.mapped('employee_id')
    #
    #     # recordset = self.sudo().search([('date', '=', date_tocheck[0]), ('employee_id.name', '=', employee_check.name)])
    #     # employee_check = self.mapped('employee_id.name')
    #
    #     # recordset = self.sudo().search([('date', '=', date_tocheck[0]), ('employee_id.id', '=', self.employee_id.id)])
    #     recordset = self.sudo().search([('date', '=', date_tocheck), ('employee_id.id', '=', self.employee_id.id)])[0]
    #     today = date.today()
    #     timeoff = 3
    #     for record in self:
    #      if record.task_id.id != timeoff:
    #        if record.date > today:
    #            raise AccessError(_("You cannot add timesheets next dates."))
    #     for record in recordset:
    #         if record.is_request == False and record.is_leave == False:
    #                 total.append(record.unit_amount)
    #         if record.is_request:
    #             ess_total.append(record.unit_amount)
    #
    #     # recordprojects = self.sudo().search([('task_id', '=', task_check.id), ('employee_id.name', '=', employee_check.name)])
    #     recordprojects = self.sudo().search([('task_id', '=', task_check.id), ('employee_id.id', '=', self.employee_id.id)])
    #     for record in recordprojects:
    #         total_planned.append(record.unit_amount)
    #
    #     # if (sum(ess_total) > 8 and self.is_timesheet == True) or\
    #     #     (self.is_timesheet == False and self.is_request == True and sum(total + ess_total) > 8):
    #
    #     # for rec in self:
    #     #     if (sum(total+ess_total) > 8 and rec.is_timesheet == True and rec.is_request == True and rec.validated_statu == 'draft') \
    #     #             or (sum(total) > 8 and rec.is_timesheet == True and rec.validated_statu == 'draft')\
    #     #             or (rec.is_timesheet == True and rec.is_request == False and sum(total) > 8):
    #     #
    #     #         # self.is_request = False
    #     #         raise ValidationError("Warning : You can't submit more than 8 hours per day")
    #
    #     if task_check.id and planned !=0:
    #         if sum(total_planned) > planned:
    #             raise ValidationError("Warning: You can't submit more planned hours for this Task")
    #     if 'unit_amount' in value:
    #         if self.unit_amount <= 0:
    #             raise ValidationError("Your time spent Can't be zero ")
    #         if not self.validated_statu == 'draft' and self.is_request == False: #in ['b', 'c', 'd', 'e']
    #             raise ValidationError("You Can't Update TimeSheet line/s amount ")
    #
    #     records = self.env['hr.employee.public'].search([('id', '=', self.employee_id.id)])
    #     for record_emp in records.resource_calendar_id:
    #         # for item in record_emp.resource_calendar_id:
    #             for order in record_emp.attendance_ids:
    #                 result.append(dict(order._fields['dayofweek'].selection).get(order.dayofweek))
    #             # for line in record_emp.global_leave_ids:
    #             #     if (self.date >= line.date_from.date()) and (self.date <= line.date_to.date()):
    #             #         raise ValidationError("Warning : You Can't Make Timesheet, You need an Approve .")
    #     if self.is_request == False and self.is_timesheet and self.validated_statu == 'draft' :  #
    #         if (self.date.strftime("%A") not in result):
    #             raise ValidationError("Warning : this is weekend, please you need an approve.")
    #     return res
        
        


    @api.depends('validated')
    def _compute_validated_status(self):
        for line in self:
            if line.validated:
                line.validated_status = 'validated'
            else:
                line.validated_status = 'draft'

    # @api.depends('validated')
    # def _compute_validated_statu(self):
    #     for line in self:
    #         if line.validated:
    #             line.validated_statu = 'validated'
    #         else:
    #             print("stateeeeeeeee")

    def action_draft(self):
        self.employee_id.reject_validation = False
        self.validated_statu = 'draft'

    def action_submit(self):
        for rec in self:
            rec.validated_statu = 'submit'
            print(self.validated_statu,'statussssss')

    def action_approve(self):
        for rec in self:
            # if rec.project_id == True:
                if rec.project_id == True and self.env.user == rec.employee_id.user_id:
                    raise ValidationError("Please You Can't Approve Your TimeSheet  ")
                else:
                    if rec.two_approve_tm or (rec.two_approve_tm and rec.one_approve_tm):
                        rec.validated_statu = 'approved'
                    elif rec.one_approve_tm:
                        rec.validated_statu = 'validated'
                        rec.validated = True

    def action_validate(self):
        for rec in self:
            if rec.project_id == True and self.env.user == rec.employee_id.user_id:
                raise ValidationError("Please You Can't Validate Your TimeSheet  ")
            else:
                rec.validated_statu = 'validated'
                rec.validated = True

    def action_canccel(self):
        for rec in self:
            if rec.project_id == True and self.env.user == rec.employee_id.user_id:
                raise ValidationError("Please You Can't Reject Your TimeSheet ")
            else:
                rec.validated_statu = 'rejected'

    # def action_reset_rejected(self):
    #     self.employee_id.reject_validation = False


    def submit_your_timesheet(self):
        all_objs = self.env['account.analytic.line'].sudo().search([('employee_id.user_id', '=', self.env.user.id),
                                                             ('validated_statu', '=', 'draft'), ('unit_amount', '<=', 8)])
        if all_objs:
            for object in all_objs:
                object.validated_statu = 'submit'
                # object.sudo().update({
                # 'validated_statu': 'b',
                #
                # })
        else:
            raise ValidationError(_("you don't have any draft lines now. "))

    def validate_timesheet(self):
        for rec in self:
            if rec.project_id == True:
                flag = self.env['res.users'].has_group('custom_bbi_timesheet.timesheet_project_manager_id')
                if flag:
                    if self.env.user != rec.employee_id.user_id:
                        if rec.validated_statu == 'approved':
                            rec.validated_statu = 'validated'
                            rec.validated = True
                        else:
                            raise ValidationError("You Can only Validate The Approved TimeSheets line/s ")
                    else:
                        raise ValidationError("Please You Can't Validate Your own TimeSheet line/s  ")
                else:
                    raise UserError('This Action for Project Manager ')

    def approve_timesheet(self):
        for rec in self:
            #if rec.project_id == True:
                flag = self.env['res.users'].has_group('custom_bbi_timesheet.timesheet_technical_manager_id')
                if flag:
                    if self.env.user != rec.employee_id.user_id:
                        if rec.validated_statu == 'submit':
                            if rec.two_approve_tm or (rec.two_approve_tm and rec.one_approve_tm):
                                rec.validated_statu = 'approved'
                            elif rec.one_approve_tm:
                                rec.validated_statu = 'validated'
                                rec.validated = True
                        else:
                            raise ValidationError("Please You Can Approve Only Submit TimeSheet line/s  ")
                    else:
                        raise ValidationError("Please You Can't Approve Your own TimeSheet line/s  ")
                else:
                    raise UserError('This Action for Direct Manager ')
     
    def reject_timesheet(self):
        for rec in self:
            dm_group = self.env['res.users'].has_group('custom_bbi_timesheet.timesheet_technical_manager_id')
            pm_group = self.env['res.users'].has_group('custom_bbi_timesheet.timesheet_project_manager_id')
            view_id = self.env.ref('custom_bbi_timesheet.view_inherit_timesheet_rejected')
            if dm_group or pm_group:
                action = {
                    'name': _('Reject Confirm'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(view_id.id, 'form')],
                    'res_model': 'reject.timesheet.wizard',
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                    'context': {'ids': self.ids, }
                }
                return action
            else:
                raise ValidationError(_("This action for direct manager or project manager"))

    def project_manger_validate(self):
        view_id = self.env.ref('timesheet_grid.timesheet_view_form')
        tree_id = self.env.ref('hr_timesheet.timesheet_view_tree_user')
        project_manger = self.env['res.users'].search(
            [('id', '=', self.env.user.id),
             ('groups_id', '=', self.env.ref('custom_bbi_timesheet.timesheet_project_manager_id').id)], limit=1)
        print(project_manger.name)
        projects = self.env["project.project"].search([('user_id', '=', project_manger.id)]).mapped("name")
        print(projects)

        if projects:
            return {
                'name': _('Project Manager Validate'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'list,form',
                'view_id': view_id.id,
                'views': [(tree_id.id, 'list'), (view_id.id, 'form')],
                'res_model': 'account.analytic.line',
                'target': 'current',
                'domain': [('project_id.name', 'in', projects), ('validated_statu', '=', 'approved')],
                # 'context': {'group_by': ['main_parent_id', 'parent_id']}
            }
        else:
            raise ValidationError(_("You Don't Have Project To Manage"))

    def manager_approve(self):
        view_id = self.env.ref('timesheet_grid.timesheet_view_form')
        tree_id = self.env.ref('hr_timesheet.timesheet_view_tree_user')
        project_manger = self.env['res.users'].search(
            [('id', '=', self.env.user.id),
             ('groups_id', '=', self.env.ref('custom_bbi_timesheet.timesheet_technical_manager_id').id)], limit=1)
        print(project_manger.name)
        # projects = self.env["project.project"].search([('user_id', '=', project_manger.id)]).mapped("name")
        # print(projects)
        submitted_users = self.env['hr.employee'].search([('timesheet_manager_id', '=', self.env.user.id)])
        if project_manger and submitted_users :
            return {
                'name': _('Project Manager Approve'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'list,form',
                'view_id': view_id.id,
                'views': [(tree_id.id, 'list'), (view_id.id, 'form')],
                'res_model': 'account.analytic.line',
                'target': 'current',
                'domain': [('employee_id', 'in', submitted_users.ids), ('validated_statu', '=', 'submit')],
                # 'context': {'group_by': ['main_parent_id', 'parent_id']}
            }
        else:
            raise ValidationError(_("You Don't Have permission"))




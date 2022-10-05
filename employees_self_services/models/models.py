# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
import dateutil.parser
import requests
from odoo.exceptions import ValidationError,UserError


all_list = []
class EmployeeSelfServices(models.Model):
    _name = 'employee.self.services'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'rating.mixin']
    _rec_name = 'task_id'



    @api.onchange('task_id')
    def _onchange_task_id(self):
        if not self.project_id:
            self.project_id = self.task_id.project_id

    project_id = fields.Many2one('project.project',
                                 string='Project',
                                 required=True,
                                 index=True,
                                 track_visibility='onchange',
                                 change_default=True)

    task_id = fields.Many2one('project.task',string='Task',
                              domain="[('project_id', '=', project_id)]", track_visibility='onchange')

    employee_id = fields.Many2one('hr.employee', "Employee", default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)]))
    name = fields.Char(related='employee_id.name')
    user_id = fields.Many2one('res.users', string='User',track_visibility='onchange',
                              default=lambda self: self.env.user)

    date = fields.Date(string='Date', required=True)
    timespent = fields.Float(string='Time Spent')
    work_id = fields.Many2one('timesheet.work_location', string="Work Location", required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('not_approved', "Waiting For Approve"), ('approved', "Approved"), ('rejected', "Rejected")], default='not_approved', string="State", track_visibility='onchange')



    def approved(self):
        for rec in self:
            flag = self.env['res.users'].has_group('employees_self_services.ess_group_manager')
            if flag :
                if rec.state != 'approved':
                    rec.state = 'approved'
                    requests = rec.env['account.analytic.line'].create({
                        'name': 'This Is Request For Extra Timesheet',
                        'account_id': rec.project_id.analytic_account_id.id,
                        'is_request': True,
                        'is_timesheet': False,
                        'project_id': rec.project_id.id,
                        'task_id': rec.task_id.id,
                        'employee_id': rec.employee_id.id,
                        'date': rec.date,
                        'unit_amount': rec.timespent,
                        'work_id': rec.work_id.id,
                        'validated_statu': 'approved',
                        })
                else:
                    raise UserError('Already approved ')
            else:
                raise UserError('You do not have permission to approve ')

    def rejected(self):
        for rec in self:
            flag = self.env['res.users'].has_group('employees_self_services.ess_group_manager')
            if flag:
                rec.state = 'rejected'
            else:
                raise UserError('You do not have permission to Reject ')

    def rest_to_wait(self):
        for rec in self:
            rec.state = 'not_approved'



class LimitEmployeeTimesheet(models.Model):
    _inherit = 'account.analytic.line'

    work_id = fields.Many2one('timesheet.work_location', string="Work Location")

    # @api.model
    # def create(self, values):
    #     result = []
    #     res = super(LimitEmployeeTimesheet, self).create(values)
    #     if values.get('product_id', True):
    #         records = self.env['hr.employee'].search([('name', '=', res['employee_id'].name)])
    #         for record in records:
    #             for item in record.resource_calendar_id:
    #                 for order in item.attendance_ids:
    #                     result.append(dict(order._fields['dayofweek'].selection).get(order.dayofweek))
    #                 for line in item.global_leave_ids:
    #                     if (res['date'] >= line.date_from.date()) and (res['date'] <= line.date_to.date()):
    #                         raise ValidationError("Warning : You Can't Make Timesheet, You need an Approve .")
    #         if res['is_request'] == False and res['is_timesheet']:
    #             if (res['date'].strftime("%A") not in result):
    #                 raise ValidationError("Warning : this is weekend, please you need an approve.")
    #
    #     return res

class timesheet_work_location(models.Model):
    _name = 'timesheet.work_location'

    name = fields.Char(string="Work Location")






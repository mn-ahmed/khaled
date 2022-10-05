# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, Warning


class leave_encash_process(models.TransientModel):
    _name = 'leave.encash.process'
    _description = 'Leave Encash Process'

    name = fields.Char(string='Month', required=True)
    department_ids = fields.Many2many('hr.department', string="Department")
    job_position_ids = fields.Many2many('hr.job', string="Job Position")
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    leave_encash_lines_ids = fields.One2many("leave.encash.lines",
                                             "leave_encash_lines_id", string="Leave Encash Lines")
    encashment_type = fields.Selection([('day_salary', 'Day Salary'), ('day_fixed', 'Day Fixed')],
                                         string="Encashment Type")
    amount = fields.Float(string="Amount")

    @api.multi
    def create_encashment(self):
        number_of_days = 0
        list_working = []
        if self.encashment_type:
            for each in self.leave_encash_lines_ids:
                emp_dept = self.env['hr.employee'].search([('id', '=', each.employee_id.id)])
                if self.encashment_type == 'day_fixed' and each.encash_leave:
                    if self.amount <= 0:
                        raise Warning(_("Please fill the fixed amount."))
                    self.env['leave.encash'].create({
                        'employee_id': each.employee_id.id,
                        'department_id': emp_dept.department_id.id,
                        'job_id': emp_dept.job_id.id,
                        'leave_carry': each.encash_leave,
                        'amount': (self.amount * (each.encash_leave)),
                        'leave_type_id': each.leave_type_id.id
                    })
                elif self.encashment_type == 'day_salary' and each.encash_leave:
                    day_salary_amt = self.env['hr.contract'].search([('employee_id', '=', each.employee_id.id)])
                    if not day_salary_amt:
                        raise ValidationError(_('Please configure contract for this customer!!!'))
                    working_days = each.employee_id.resource_calendar_id.attendance_ids
                    for working in working_days:
                        number_of_working_days = 0
                        if int(working.dayofweek) not in list_working :
                            list_working.append(int(working.dayofweek))
                    first_date = date.today() + relativedelta(day=1)
                    last_date = date.today() + relativedelta(day=1, months=+1, days=-1)
                    delta = last_date - first_date
                    for i in range(delta.days + 1):
                        date_range = (first_date + timedelta(days=i))
                        week_day = date_range.weekday()
                        if week_day in list_working:
                            number_of_working_days += 1
                    for per_day_amt in day_salary_amt:
                        self.env['leave.encash'].create({
                            'employee_id' : each.employee_id.id,
                            'department_id': emp_dept.department_id.id,
                            'job_id': emp_dept.job_id.id,
                            'leave_carry': each.encash_leave,
                            'amount': ((per_day_amt.wage / number_of_working_days) * (each.encash_leave)),
                            'leave_type_id': each.leave_type_id.id
                        })
        else:
            raise Warning(_("Please select Encashment Policy."))

    @api.onchange('department_ids', 'job_position_ids', 'leave_type_id')
    def search_employee(self):
        leave_encash = 0
        list = []
        emp_ids = self.env['hr.employee'].sudo().search([('department_id', 'in', self.department_ids.ids),
                                                          ('job_id', 'in', self.job_position_ids.ids)
                                                          ])
        leave_encash_settings = self.env['res.config.settings'].sudo().search([], limit=1, order='id DESC')
        for emp in emp_ids:
            allocated_days = 0
            removed_days = 0
            total_leave_pending = 0
            leave_status_add = self.env['hr.leave.allocation'].sudo().search([('employee_id.id', '=', emp.id),
                                                               ('holiday_status_id', '=', self.leave_type_id.id),
                                                               ('state', '=', 'validate')])
            leave_status_remove = self.env['hr.leave'].sudo().search([('employee_id.id', '=', emp.id),
                                                                      ('state', '=', 'validate'),
                                                                      ('holiday_status_id', '=', self.leave_type_id.id)
                                                                      ])
            if emp.job_id.encash_leave >= 1.0:
                leave_encash = emp.job_id.encash_leave
            else:
                leave_encash = leave_encash_settings.encash_leave
            for add in leave_status_add:
                allocated_days += add.number_of_days
            for remove in leave_status_remove:
                removed_days += remove.number_of_days
            total_leave_pending = allocated_days - removed_days
            encashed_employee = self.env['leave.encash'].sudo().search([('employee_id', '=', emp.id),
                                                                        ('leave_type_id', '=', self.leave_type_id.id)
                                                                        ])
            for employee_encashed in encashed_employee:
                if employee_encashed.state != 'cancel':
                    total_leave_pending -= employee_encashed.leave_carry
            if total_leave_pending > 0:
                if  total_leave_pending >= leave_encash:
                    list.append((0, 0, {
                                      'employee_id'   : emp.id,
                                      'leave_type_id' : self.leave_type_id.id,
                                      'pending_leave' : total_leave_pending,
                                      'encash_leave'  : leave_encash
                                    }))
                elif  total_leave_pending < leave_encash and total_leave_pending > 0:
                      leave_encash = total_leave_pending
                      list.append((0, 0, {
                                        'employee_id'   : emp.id,
                                        'leave_type_id' : self.leave_type_id.id,
                                        'pending_leave' : total_leave_pending,
                                        'encash_leave'  : leave_encash
                                    }))
                else:
                   leave_encash = leave_encash_settings.encash_leave
                   list.append((0, 0, {
                                     'employee_id'   : emp.id,
                                     'leave_type_id' : self.leave_type_id.id,
                                     'pending_leave' : total_leave_pending,
                                     'encash_leave'  : 0
                                }))

                self.update({'leave_encash_lines_ids': list})


    @api.multi
    def search_leave(self):
        leave_encash = 0
        dept_ids = self.department_ids.ids  if self.department_ids else self.env['hr.department'].search([]).ids
        job_ids = self.job_position_ids.ids if self.job_position_ids else self.env['hr.job'].search([]).ids
        
        
        employee_ids = self.env['hr.employee'].sudo().search(['|',('department_id', 'in', dept_ids or []),
                                                               ('job_id', 'in', job_ids or [])])
        
        leave_encash_settings = self.env['res.config.settings'].sudo().search([], limit=1, order='id DESC')
        list = []
        if self.leave_type_id:
            each_status = self.leave_type_id
            for employee in employee_ids:
                    allocated_days = 0
                    removed_days = 0
                    total_leave_pending = 0
                    leave_status_add = self.env['hr.leave.allocation'].sudo().search([('employee_id.id', '=', employee.id),
                                                                                      ('holiday_status_id', '=', each_status.id),
                                                                                      ('state', '=', 'validate'),
                                                                                     ])

                    leave_status_remove = self.env['hr.leave'].sudo().search([('employee_id.id', '=', employee.id),
                                                                              ('holiday_status_id', '=', each_status.id),
                                                                              ('state', '=', 'validate'),
                                                                              ])
                    if employee.job_id.encash_leave > 0:
                            leave_encash = employee.job_id.encash_leave
                    else:
                         leave_encash = leave_encash_settings.encash_leave

                    for add in leave_status_add:
                        allocated_days += add.number_of_days
                    for remove in leave_status_remove:
                        removed_days += remove.number_of_days
                    total_leave_pending = allocated_days - removed_days
                    encashed_ids = self.env['leave.encash'].sudo().search([('employee_id', '=', employee.id),
                                                                           ('leave_type_id', '=', each_status.id)
                                                                         ])
                    for employee_encashed in encashed_ids:
                        if employee_encashed.state != 'cancel':
                            total_leave_pending -= employee_encashed.leave_carry

                    if total_leave_pending > 0:
                        if  total_leave_pending >= leave_encash:
                            leave_dict = {
                                          'employee_id': employee.id,
                                          'leave_type_id': each_status.id,
                                          'pending_leave': total_leave_pending,
                                          'encash_leave': leave_encash
                                    }
                        elif total_leave_pending < leave_encash:
                                leave_encash = total_leave_pending
                                leave_dict = {
                                              'employee_id': employee.id,
                                              'leave_type_id': each_status.id,
                                              'pending_leave': total_leave_pending,
                                              'encash_leave': leave_encash
                                        }
                        if leave_dict not in list:
                            list.append((0, 0, leave_dict))
            self.update({'leave_encash_lines_ids': list})

        else:
            holiday_status_ids = self.env['hr.leave.type'].sudo().search([])
            leave_encash_settings = self.env['res.config.settings'].sudo().search([], limit=1, order='id DESC')
            list = []
            for each_status in holiday_status_ids:
                for employee in employee_ids:
                    allocated_days = 0
                    removed_days = 0
                    total_leave_pending = 0

                    leave_status_add = self.env['hr.leave.allocation'].sudo().search([
                                                                       ('employee_id.id', '=', employee.id),
                                                                       ('holiday_status_id', '=', each_status.id),
                                                                       ('state', '=', 'validate'),
                                                                    ])
                    leave_status_remove = self.env['hr.leave'].sudo().search([
                                                                          ('employee_id.id', '=', employee.id),
                                                                          ('holiday_status_id', '=', each_status.id),
                                                                          ('state', '=', 'validate'),
                                                                        ])

                    if employee.job_id.encash_leave > 0:
                        leave_encash = employee.job_id.encash_leave
                    else:
                         leave_encash = leave_encash_settings.encash_leave
                    for add in leave_status_add:
                        allocated_days += add.number_of_days
                    for remove in leave_status_remove:
                        removed_days += remove.number_of_days
                    total_leave_pending = allocated_days - removed_days

                    encashed_ids = self.env['leave.encash'].sudo().search([
                                                     ('employee_id', '=', employee.id),
                                                     ('leave_type_id', '=', each_status.id)])
                    for employee_encashed in encashed_ids:
                        if employee_encashed.state != 'cancel':
                            total_leave_pending -= employee_encashed.leave_carry
                    if total_leave_pending > 0:
                       if  total_leave_pending >= leave_encash:
                           leave_dict = {
                                        'employee_id': employee.id,
                                        'leave_type_id': each_status.id,
                                        'pending_leave': total_leave_pending,
                                        'encash_leave': leave_encash
                                    }
                       elif total_leave_pending < leave_encash:
                           leave_encash = total_leave_pending
                           leave_dict = {
                                         'employee_id': employee.id,
                                         'leave_type_id': each_status.id,
                                         'pending_leave': total_leave_pending,
                                         'encash_leave': leave_encash
                           }
                       if leave_dict not in list:
                           list.append((0, 0, leave_dict))
            self.update({'leave_encash_lines_ids': list})

class leave_encash_lines(models.TransientModel):
    _name = 'leave.encash.lines'
    _description = 'Leave Encash Lines'

    @api.one
    @api.constrains('encash_leave')
    def _check_max_term(self):
        if self.encash_leave != 0 and self.encash_leave > self.pending_leave:
            raise ValidationError(_('Encash leave should be less then Pending Leaves.'))

    employee_id = fields.Many2one('hr.employee', string="Employee")
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    pending_leave = fields.Float(string="Pending Leaves")
    encash_leave = fields.Float(string="Encash Leave")
    leave_encash_lines_id = fields.Many2one("leave.encash.process")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4

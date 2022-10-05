# -*- coding: utf-8 -*-


from odoo import models, fields, api
from datetime import datetime, date, timedelta
import calendar


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    timesheet_week = fields.Char('Timesheet Last Week')

    def get_last_week_date_list(self):
        lst = []
        cur_date = date.today()
        for i in [-7, -6, -5, -4, -3]:
            n_date = cur_date + timedelta(days=i)
            n_date = n_date.strftime('%Y-%m-%d')
            lst.append(n_date)
        return lst

    def send_mail_timesheet_reminder(self, employee):
        mtp = self.env['mail.template']
        template_id = self.env.ref('dev_timesheet_reminder.timesheet_reminder_mail_template').id
        print("------------template_id------------",)
        mail_tem = mtp.browse(template_id)
        mail_tem.send_mail(employee.id, True)
        return True

    def get_timesheet_summary(self, employee):
        account_ana_pool = self.env['account.analytic.line']
        date_list = self.get_last_week_date_list()
        timesheet_table = []
        for date_l in date_list:
            timesheet_ids = account_ana_pool.search(
                [('employee_id', '=', employee.id), ('date', '=', date_l)])
            total_hour = 0
            date_l = datetime.strptime(date_l, '%Y-%m-%d')
            date_l = date_l.strftime('%d-%m-%Y')
            if timesheet_ids:
                for timesheet_id in timesheet_ids:
                    total_hour += timesheet_id.unit_amount
                if total_hour < 8:
                    timesheet_table.append({'date_l': str(date_l or ' '),
                                            'total_hour': str(total_hour or ' '),
                                           })
            else:
                timesheet_table.append({'date_l':str(date_l or ' '),
                                        'total_hour' : str('Not Fill'),
                                       })
        return timesheet_table

    def get_timesheet_last_week(self, date_list):
        s_date = date_list[0]
        e_date = date_list[-1]
        s_date = datetime.strptime(s_date, '%Y-%m-%d')
        s_date = s_date.strftime('%d-%m-%Y')
        e_date = datetime.strptime(e_date, '%Y-%m-%d')
        e_date = e_date.strftime('%d-%m-%Y')
        return str(s_date) + ' TO ' + str(e_date)

    def send_timesheet_reminder(self):
        account_ana_pool = self.env['account.analytic.line']
        day_name = calendar.day_name[date.today().weekday()]
        if day_name == 'Monday':
            employee_ids = self.env['hr.employee'].search(
                [('active', '=', True)])
            date_list = self.get_last_week_date_list()
            for employee in employee_ids:
                count = 0
                for date_l in date_list:
                    timesheet_ids = account_ana_pool.search(
                        [('employee_id', '=', employee.id),
                         ('date', '=', date_l)])
                    print("------timesheet_ids-------------",timesheet_ids)
                    total_hour = 0
                    if timesheet_ids:
                        for timesheet_id in timesheet_ids:
                            total_hour += timesheet_id.unit_amount
                        if total_hour < 8:
                            count += 1
                    else:
                        count += 1
                if count > 0:
                    employee.timesheet_week = self.get_timesheet_last_week(
                        date_list)
                    self.send_mail_timesheet_reminder(employee)



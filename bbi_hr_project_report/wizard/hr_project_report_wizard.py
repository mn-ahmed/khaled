import io
import math
from datetime import datetime, timedelta

import xlsxwriter

from odoo import models, fields, api
from odoo.tools.float_utils import float_round


class HrProjectReportWizard(models.TransientModel):
    _name = 'hr.project.report.wizard'

    date_start = fields.Date(string="Start Date", )
    date_end = fields.Date(string="End Date", )
    project_id = fields.Many2one('project.project', string='Project', required=True)

    def action_download_hr_project_report_wizard(self):
        return {
            'type': "ir.actions.act_url",
            'target': "self",
            'url': "/web/content/download/hr_project_report/{date_start}/{date_end}/{project}".format(
                date_start=str(self.date_start), date_end=str(self.date_end), project=self.project_id.id
            )
        }

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days + 1)):
            yield start_date + timedelta(n)

    def get_hr_project_report(self, response, date_start, date_end, project):
        start_date = datetime.strptime(date_start, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_end, '%Y-%m-%d').date()
        leave_project_id = self.env['project.project'].search(
            [
                ('is_leave_project', '=', True)
            ])
        timesheet_objects = self.env['account.analytic.line'].search(
            [
                ('project_id', '=', project.id),
                ('date', '>=', start_date),
                ('date', '<=', end_date),
            ]
        )
        employee_list = timesheet_objects.mapped('employee_id')
        print('employee_list = ', employee_list)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'strings_to_formulas': False, })
        date_format = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'num_format': 'd mmm yyyy'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': '#071f75', 'font_size': 14, 'color': 'white', 'bold': True,
             'left': 1,
             'bottom': 1,
             'right': 1, 'top': 1,
             'align': 'center'})
        merge_format_cell1 = workbook.add_format({
            'font_name': 'Times',
            'color': 'white',
            'font_size': 14,
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#071f75'})
        merge_format = workbook.add_format({
            'font_name': 'Times',
            'color': 'white',
            'font_size': 14,
            'bold': 1,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'fg_color': '#071f75'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'font_size': 12, 'border': 1, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'center'})
        for employee in employee_list:
            resource_calendar_id = employee.resource_calendar_id
            emp_attendance_ids = resource_calendar_id.attendance_ids
            emp_dayofweek = [attendance.dayofweek for attendance in emp_attendance_ids]
            emp_global_leave_list = []
            if resource_calendar_id.global_leave_ids:
                for global_leave in resource_calendar_id.global_leave_ids:
                    emp_global_leave_list.extend(list(self.daterange(global_leave.date_from.date(),
                                                                 global_leave.date_to.date())))
            print(emp_global_leave_list)
            sheet = workbook.add_worksheet(name='"%s" Sheet' % employee.name)
            sheet.set_default_row(25)
            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 40)
            sheet.set_column(2, 2, 20)
            sheet.set_column(3, 3, 20)
            sheet.merge_range('A1:B1', 'Name', merge_format_cell1)
            sheet.merge_range('A2:B2', 'Project', merge_format_cell1)
            sheet.merge_range('A3:B3', '# Days', merge_format_cell1)
            sheet.merge_range('C1:D1', employee.name, merge_format)
            sheet.merge_range('C2:D2', project.name, merge_format)
            sheet.merge_range('C3:D3', len(timesheet_objects), merge_format)
            sheet.write(3, 0, '#', header_style)
            sheet.write(3, 1, 'Date', header_style)
            sheet.write(3, 2, 'From', header_style)
            sheet.write(3, 3, 'To', header_style)
            row = 4
            counter = 1
            for single_date in self.daterange(start_date, end_date):
                name_of_date = single_date.strftime('%A , %b %d , %Y')
                employee_project_timesheet_objects = self.env['account.analytic.line'].search(
                    [
                        ('employee_id', '=', employee.id),
                        ('project_id', '=', project.id),
                        ('date', '>=', single_date),
                        ('date', '<=', single_date),
                    ], limit=1
                )
                employee_leave_timesheet_objects = self.env['account.analytic.line'].search(
                    [
                        ('employee_id', '=', employee.id),
                        ('project_id', '=', leave_project_id.id),
                        ('date', '=', single_date),
                    ], limit=1
                )
                if str(single_date.weekday()) in emp_dayofweek:
                    if single_date in emp_global_leave_list:
                        sheet.write(row, 0, counter, number_style)
                        sheet.write(row, 1, name_of_date, date_format)
                        sheet.write(row, 2, 'Public Leave', number_style)
                        sheet.write(row, 3, 'Public Leave', number_style)
                        counter += 1
                        row += 1

                    elif len(employee_project_timesheet_objects) > 0:
                        for employee_project_sheet in employee_project_timesheet_objects:
                            sheet.write(row, 0, counter, number_style)
                            sheet.write(row, 1, name_of_date, date_format)
                            sheet.write(row, 2, employee_project_sheet.from_time, number_style)
                            sheet.write(row, 3, employee_project_sheet.to_time, number_style)
                        counter += 1
                        row += 1

                    else:

                        if employee_leave_timesheet_objects:
                            sheet.write(row, 0, counter, number_style)
                            sheet.write(row, 1, name_of_date, date_format)
                            sheet.write(row, 2, 'Time Off', number_style)
                            sheet.write(row, 3, 'Time Off', number_style)
                            counter += 1
                            row += 1


                        else:
                            sheet.write(row, 0, counter, number_style)
                            sheet.write(row, 1, name_of_date, date_format)
                            sheet.write(row, 2, 'Missed', number_style)
                            sheet.write(row, 3, 'Missed', number_style)
                            counter += 1
                            row += 1

                if str(single_date.weekday()) not in emp_dayofweek:
                    sheet.write(row, 0, counter, number_style)
                    sheet.write(row, 1, name_of_date, date_format)
                    sheet.write(row, 2, 'Week Holiday', number_style)
                    sheet.write(row, 3, 'Week Holiday', number_style)
                    counter += 1
                    row += 1

        workbook.close()
        output.seek(0)
        generated_file = response.stream.write(output.read())
        output.close()

        return generated_file

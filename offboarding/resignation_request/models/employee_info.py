from odoo import models, fields, api ,_


class EmployeeProject(models.Model):
    _name = 'employee.project'

    name = fields.Char(string="Name", copy=False, required=True)


class EmployeeInfo(models.Model):
    _inherit = 'hr.employee'

    employee_project = fields.Many2many('employee.project', string="Project", groups="hr.group_hr_user")
    employee_project_manager = fields.Many2one('hr.employee', string="Project Manager", groups="hr.group_hr_user")



class EmployeePublicInfo(models.Model):
    _inherit = 'hr.employee.public'

    employee_project = fields.Many2many('employee.project', string="Project")
    employee_project_manager = fields.Many2one('hr.employee', string="Project Manager")




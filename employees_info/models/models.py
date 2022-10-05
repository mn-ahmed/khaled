# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeesInfopublic(models.Model):
    _inherit = 'hr.employee.public'


    employee_full_name = fields.Char('Employee Full Name')
    latest_employer = fields.Char('Latest Employer')
    previous_employer = fields.Char('Previous Employer')
    previous_employers = fields.Char('Previous Employers')
    experience = fields.Integer(string='Experience')
    graduation_year = fields.Integer(string='Graduation Year')
    address_home_id = fields.Many2one('res.partner', 'Address',
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    birthday = fields.Date('Date of Birth')
    #grade_id = fields.Many2one('hr.grade.cost', string="Grade")

class EmployeesInfo(models.Model):
    _inherit = 'hr.employee'

    employee_status = fields.Many2one('employee.status', string="Employee Status", groups="hr.group_hr_user")
    family_status = fields.Many2one('family.status', string="Family Status", groups="hr.group_hr_user")
    number_of_dependants_company = fields.Integer(string='Number of dependants covered by company', groups="hr.group_hr_user")
    number_of_dependants_employee = fields.Integer(string="Number of dependants covered by employee", groups="hr.group_hr_user")
    employment_type = fields.Many2one('employment.type', string="Employment Type", groups="hr.group_hr_user")
    employee_full_name = fields.Char('Employee Full Name')
    latest_employer = fields.Char('Latest Employer')
    previous_employer = fields.Char('Previous Employer')
    previous_employers = fields.Char('Previous Employers')
    employee_level = fields.Many2one('employee.level', string="Level", groups="hr.group_hr_user")
    employee_percentile = fields.Many2one('employee.percentile', string="Percentile", groups="hr.group_hr_user")
    experience = fields.Integer(string='Experience')
    graduation_year = fields.Integer(string='Graduation Year')
    basic_salary = fields.Integer(string='المرتب الاساسي' , groups="hr.group_hr_user")
    Variable_salary = fields.Integer(string='المرتب المتغير', groups="hr.group_hr_user")
    insurance_status = fields.Many2one('insurance.status', string="حالة التأمين" , groups="hr.group_hr_user")
    insurance_number = fields.Integer(string='الرقم التأميني', groups="hr.group_hr_user")
    insurance_bureau = fields.Many2one('insurance.bureau', string="مكتب التأمين المؤمن به", groups="hr.group_hr_user")
    institution_number = fields.Integer(string='رقم المنشأة' , groups="hr.group_hr_user")
    insurance_date = fields.Date(string='تاريخ التأمين', groups="hr.group_hr_user")


class EmployeesStatus(models.Model):
    _name = 'employee.status'

    name = fields.Char('Name', required=True, )


class FamilyStatus(models.Model):
    _name = 'family.status'

    name = fields.Char('Name', required=True,)


class EmploymentType(models.Model):
    _name = 'employment.type'

    name = fields.Char('Name', required=True, translate=True)


class EmployeeLevel(models.Model):
    _name = 'employee.level'

    name = fields.Char('Name', required=True, translate=True)


class EmployeePercentile(models.Model):
    _name = 'employee.percentile'

    name = fields.Char('Name', required=True, translate=True)


class InsuranceStatus(models.Model):
    _name = 'insurance.status'

    name = fields.Char('Name', required=True, translate=True)


class InsuranceBureau(models.Model):
    _name = 'insurance.bureau'

    name = fields.Char('Name', required=True, translate=True)


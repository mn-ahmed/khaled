
{
    'name': 'Human Resource Solution',
    'category': 'HR',
    'description': """
                   Flexi HR provides a complete solution for services related to Human Resources 
                   and it's relevant perspectives.
                 """,
    'summary': 'Manage Employee Loan, payroll, '
               'recruitment processes, employee contracts, '
               'employee attendance, employee timesheet,'
               ' mass leave allocation and leave management, '
               'business trip request.',
    'author': 'BBI_consultancy',
    'website': 'http://www.bbi-consultancy.com.com',
    'images': [

    ],
    'depends': ['base', 'stock', 'account',
                'hr_payroll', 'hr', 'hr_attendance',
                'hr_contract', 'hr_recruitment','hr_expense','employees_self_services'
                ],
    'images': [],
    'data': [

        #leave encashment
        # 'leave_encash/security/leave_security.xml',
        # 'leave_encash/views/hr_job_views.xml',
        # 'leave_encash/wizard/leave_encash_process_views.xml',
        # 'leave_encash/views/leave_config_setting_views.xml',
        # 'leave_encash/views/leave_encash_views.xml',
        # 'leave_encash/views/hr_payroll_views.xml',
        # 'leave_encash/views/hr_payroll_data.xml',
        # 'leave_encash/views/report.xml',
        # 'leave_encash/wizard/leave_encash_report_wizard.xml',
        # 'leave_encash/report/leave_encash_report.xml',
        # 'leave_encash/security/ir.model.access.csv',
        # 'security/ir.model.access.csv',
        


        #travel request
        "employee_travel_request/security/aspl_hr_travel_security.xml",
        "employee_travel_request/security/ir.model.access.csv",
        "employee_travel_request/data/aspl_hr_travel_sequences.xml",
        "employee_travel_request/data/aspl_hr_travel_mail_templates.xml",
        "employee_travel_request/views/res_config_settings_views.xml",
        "employee_travel_request/views/hr_employee_view.xml",
        "employee_travel_request/views/emp_grade_expense_view.xml",
        "employee_travel_request/views/emp_grade_view.xml",
        "employee_travel_request/views/emp_travel_request_view.xml",
        "employee_travel_request/views/employee_proposed_expenses_view.xml",
        "employee_travel_request/views/emp_travel_place_view.xml",
        "employee_travel_request/views/emp_multi_currency_view.xml",
        "employee_travel_request/views/menu_views.xml",
        "employee_travel_request/wizard/hr_travel_reason_wizard.xml",



    ],
    'demo': [],
    # 'external_dependencies': {
    #     'python': [
    #         'numpy'
    #     ],
    # },
    'qweb': [
        'employee_travel_request/views/account_parent_backend.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

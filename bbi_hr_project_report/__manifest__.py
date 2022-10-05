# -*- coding: utf-8 -*-
{
    'name': "HR Project Report",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'project', 'hr_timesheet', 'timesheet_grid'],
    'data': [

        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/account_analytic_line_views.xml',
        'wizard/hr_project_report_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

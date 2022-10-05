# -*- coding: utf-8 -*-
{
    'name': "ESS",

    'summary': """
    ESS for employee self services that used to make a request for 
    entering that day in timesheet ,that day is a holiday or global leaves 
        """,

    'description': """
        Long description of module's purpose:
        this app used for limit user for timesheet depends on the work location
        you must have timesheet_work_location before installing that app
        
    """,

    'author': "My Company",
    'website': "",

    'category': 'ess',
    'version': '0.1',

    'depends': ['base', "timesheet_grid","hr_timesheet",'hr_holidays'],

    'data': [
        'security/ess_security.xml',
        'security/ir.model.access.csv',
        'security/ess_record_rules.xml',
        'security/onboarding_security.xml',
        'views/views.xml',
        'data/sequences.xml',
        'views/inherit_timesheet.xml',
        'views/views_location.xml',
        'views/ess_menus.xml',
        'views/onboarding_process.xml',
        'data/templates.xml'

    ],
    'demo': [
        'demo/demo.xml',
    ],
}
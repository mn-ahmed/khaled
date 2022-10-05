# -*- coding: utf-8 -*-
{
    'name': "Enhancement Timesheet Management BBI ",

    'summary': """Enhancement Timesheet management System""",

    'description': """
         for managing:
            - resources
            - projects
            - workflows
            


    """,
    "license": "",
    'author': "israa.elkolaly@bbi-consultancy,com",
    'website': "http://www.bbi-consultancy.com",
    'category': 'Timesheet',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'analytic',
                "hr_timesheet", 'custom_bbi_timesheet', 'timesheet_grid'],
    'images': [
    ],

    'data': [
        # 'security/ir.model.access.csv',
        # 'security/timesheet_edit.xml',
        # 'security/record_rule_for_timesheet.xml',
        'views/sec_group.xml',
        "views/inhance_timesheet.xml",

        # 'wizard/inherit_timesheet_wizard.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}

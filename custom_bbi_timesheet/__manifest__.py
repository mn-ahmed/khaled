# -*- coding: utf-8 -*-
{
    'name': "Timesheet Management BBI",

    'summary': """Timesheet management System""",

    'description': """
         for managing:
            - resources
            - projects
            - workflows
            


    """,
    "license": "AGPL-3",
    'author': "israa.elkolaly@bbi-consultancy,com",
    'website': "http://www.bbi-consultancy.com",
    'category': 'Timesheet',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web',
                "hr_timesheet", 'mail', 'timesheet_grid', 'hr', 'project', 'project_timesheet_synchro'],
    'images': [
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/timesheet_edit.xml',
        # 'security/record_rule_for_timesheet.xml',
        "views/inherit_timesheet.xml",
        # 'views/timesheet_templates.xml',
        'wizard/inherit_timesheet_wizard.xml',

    ],
    'demo': [

    ],
    'qweb': [
        "static/src/xml/custom_button.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}

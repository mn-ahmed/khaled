# -*- coding: utf-8 -*-
{
    'name': "Resignation And Off-boarding",

    'summary': """
        This is a request to manage employees resignation through odoo and it will go through
        three stages""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Israa Elkolaly <<israa.elkolaly@bbi-consultancy.com>>",

    'category': 'ESS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'employees_self_services'],

    # always loaded
    'data': [

        ### Resignation ###
        'resignation_request/security/ir.model.access.csv',
        'resignation_request/security/security_groups.xml',
        'resignation_request/views/sequence.xml',
        'resignation_request/views/employee_info_view.xml',
        'resignation_request/views/resignation_views.xml',
        'resignation_request/views/mail_templates.xml',

        ### Offboarding ###
        'offboarding_requests/security/ir.model.access.csv',
        'offboarding_requests/security/security_groups.xml',
        'offboarding_requests/views/sequence.xml',
        'offboarding_requests/views/offboarding_request_view.xml',
        'offboarding_requests/views/mail_templates.xml',

    ],

}
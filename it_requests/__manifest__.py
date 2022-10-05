# -*- coding: utf-8 -*-
{
    'name': "IT request",

    'summary': """
        VM Request
        License creation and Request""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Israa Elkolaly <israa.elkolaly@bbi-consultancy.com>",
    'category': 'ESS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','employees_self_services','sla_onboard'],

    # always loaded
    'data': [

        'vm_request/security/groups_rules.xml',
        'vm_request/security/ir.model.access.csv',
        'vm_request/data/sequence.xml',
        'vm_request/views/vm_request_view.xml',
        'vm_request/views/templates.xml',

        'license_request/security/groups_rules.xml',
        'license_request/security/ir.model.access.csv',
        'license_request/data/sequence.xml',
        'license_request/views/license_view.xml',
        'license_request/views/license_request_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

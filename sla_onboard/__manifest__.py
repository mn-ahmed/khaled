# -*- coding: utf-8 -*-
{
    'name': "Onboard SLA",

    'summary': """
        Onboard SLA """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Israa Elkolaly <<israa.elkolaly@bbi-consultancy.com>>",

    'category': 'ESS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'employees_self_services'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups_rules.xml',
        'views/onboard_sla.xml',
        'views/mail.xml',
        'views/template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
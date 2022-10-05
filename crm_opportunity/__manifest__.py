# -*- coding: utf-8 -*-
{
    'name': "CRM Opportunity",

    'summary': """
       add some fields in crm form """,

    'description': """
        Long description of module's purpose
    """,

    'author': "israa.elkolaly@bbi-consultancy.com",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'CRM',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/crm_opportunity.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
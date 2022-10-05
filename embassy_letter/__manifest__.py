# -*- coding: utf-8 -*-
{
    'name': "Embassy Letter",

    'summary': """
         request Embassy letter and submitted by manager """,

    'description': """
        user will be authorize to request Embassy letter and submitted to his Direct manager for approval 
    """,

    'author': "Israa Elkolaly <israa.elkolaly@bbi-consultancy.com>",
    # 'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ESS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','employees_self_services'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups_rules.xml',
        'data/sequence.xml',
        'views/embassy_letter_views.xml',
        'views/templates.xml',
    ],
    #only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
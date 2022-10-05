# -*- coding: utf-8 -*-
{
    'name': " Assets Error ",

    'summary': """
       solve assets error when compute deprecation , partner_bank_is get false as string  """,

    'description': """
        solve assets error when compute deprecation , partner_bank_is get false as string
    """,

    'author': "israa.elkolaly@bbi.consultancy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Assets',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/sale_form.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode

}
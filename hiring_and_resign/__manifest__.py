# -*- coding: utf-8 -*-
{
    'name': "hiring_and_resign",

    'summary': """
        Adding Hiring Date And Resigning date for Hr_employee
        """,

    'description': """
        Long description of hiring_and_resign's purpose
        to add more feature for employee to know about resigning date and hiring date
    """,

    'author': "My Company",
    'website': "http://www.BBI_consultancy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
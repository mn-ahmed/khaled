# -*- coding: utf-8 -*-
{
    'name': "Pricing Calculations",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'crm'],
    'data': [

        'security/ir.model.access.csv',
        'views/pricing_calc_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

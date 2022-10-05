# -*- coding: utf-8 -*-
{
    'name': "Financial Reports Customization",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account', 'customer_supplier'],
    'data': [

        # 'security/ir.model.access.csv',
        'views/account_move_line_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

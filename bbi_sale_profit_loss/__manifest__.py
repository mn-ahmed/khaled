# -*- coding: utf-8 -*-
{
    'name': "Sale Profit And Loss",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale'],
    'data': [

        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/sale_order_profit_loss_wizard_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

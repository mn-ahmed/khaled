# -*- coding: utf-8 -*-
{
    'name': "Crm GP Value Customization",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'crm_opportunity'],
    'data': [

        # 'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

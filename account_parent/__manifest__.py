# -*- coding: utf-8 -*-

{
    'name': "Parent Account (Chart of Account Hierarchy)",
    'summary': """
        Adds Parent account and ability to open chart of account list view based on the date and moves""",
    'description': """
This module 
        * Adds new type 'view' in account type
        * Adds parent account in account
        * Adds Chart of account hierarchy view
        * Adds credit, debit and balance in account
        * Shows chart of account based on the date and target moves we have selected
        * Provide PDF and XLS reports
    - Need to set the group show chart of account structure to view the chart of account hierarchy.
    For any support contact o4odoo@gmail.com or omalbastin@gmail.com
    """,

    'author': 'Ali Elgarhi',
    
    'license': 'OPL-1',
    'website': 'bbi-cinsulting.com',
    'category': 'Accounting',
    'version': '15.0.1.0.1',
    'depends': ['account'],
    'data': [
        'security/account_parent_security.xml',
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/open_chart.xml',
        'data/account_type_data.xml',
        # 'views/account_parent_template.xml', #moved to assests tag
        'views/report_coa_hierarchy.xml',
        #'views/res_config_view.xml'
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_common': [
            'account_parent/static/src/scss/coa_hierarchy.scss',
        ],
        'web.assets_backend': [
            'account_parent/static/src/js/account_parent_backend.js',
            'account_parent/static/src/js/account_parent_widgets.js'
        ],
        'web.assets_qweb': [
            'account_parent/static/src/xml/account_parent_backend.xml',
            'account_parent/static/src/xml/account_parent_line.xml',
            ]
    },

   
    'images': ['static/description/account_parent_9.png'],
    'installable': True,
    'post_init_hook': '_assign_account_parent',
}

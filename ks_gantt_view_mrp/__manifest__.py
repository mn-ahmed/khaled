# -*- coding: utf-8 -*-
{
	'name': 'Odoo Gantt View Manufacturing',

	'summary': """
This module provides you a Gantt View while scheduling different manufacturing tasks,
            which helps you to effectively manage your tasks with time. You can keep track of
            dependent tasks, prioritize a task over another, and see the availability of resources to
            complete a task within a time limit.
""",

	'description': """
work orders management system in odoo
        work orders in odoo
        manage / edit work orders in odoo
        odoo manufacturing app  
        odoo manufacturing module
        manufacturing module odoo
        manufacturing modules in odoo
        employee work schedule in odoo
        apps for odoo manufacturing
        manufacturing apps for odoo
        odoo work orders apps
        odoo 15 manufacturing management
        odoo manufacturing 14
        manufacturing gantt chart
        manufacturing managers odoo app
        manufacturing order management in odoo
        gantt view in work orders 
        gantt view in manufacturing
        work orders  in manufacturing module 
        manufacturing app for odoo
""",

	'author': 'Ksolves India Ltd.',

	'license': 'OPL-1',

	'currency': 'EUR',

	'price': '0',

	'live_test_url': 'http://ganttview15.kappso.in/',

	'website': 'https://store.ksolves.com',

	'maintainer': 'Ksolves India Ltd.',

	'category': 'Tools',

	'version': '15.0.1.0.0',

	'support': 'sales@ksolves.com',

	'depends': ['ks_gantt_view_base', 'mrp', 'hr'],

	'images': ['static/description/app_banner.jpg'],

	'data': ['data/data.xml', 'views/ks_mrp_production.xml', 'views/ks_mrp_production_view.xml', 'security/ir.model.access.csv', 'views/ks_mrp_gantt_settings.xml', 'views/ks_import_mrp_production.xml', 'views/ks_import_work_order.xml', 'views/ks_gantt_mrp_wo.xml'],

	'assets': {'web.assets_backend': ['ks_gantt_view_mrp/static/src/js/ks_gantt_renderer_inherit.js']},
}

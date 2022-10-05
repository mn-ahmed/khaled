# -*- coding: utf-8 -*-
{
	'name': 'Odoo Gantt View Time Off',

	'summary': """
The module helps in managing all the leaves of the employees of an organization from a centralized platform. 
        From the gantt View, one can keep track of all the leaves and manage them effectively.
""",

	'description': """
time off module in odoo
        leave management in odoo
        calendar view in odoo
        leave management odoo
        odoo leave management
        leave module odoo
        odoo leave portal
        odoo leave request
        Odoo time off app
        time off app in odoo
        manage leaves in Odoo
        odoo 15 time off management
        managing employee leaves in odoo
        leave management in odoo
        time off in odoo
        odoo leave accural
        Employees monthly leaves odoo
        time off gantt view odoo
        odoo leave gantt view
        leaves gantt view
        odoo gantt view leave app
        odoo gantt leave management
        odoo gantt view management
        odoo leave gantt view
        gantt view in odoo
        odoo project management module
        HR employee holiday in odoo
        Leaves View in odoo
        gantt view in employee leaves dashboard 
        gantt view in leaves request view.
        leave request in project module gantt chart
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

	'depends': ['ks_gantt_view_base', 'hr_holidays'],

	'images': ['static/description/app_banner.jpg'],

	'data': ['data/data.xml', 'views/ks_hr_leave_gantt_view.xml', 'views/ks_hr_leave_gantt_setting_view.xml', 'views/ks_hr_leave_form_view.xml', 'views/ks_import_holiday.xml', 'security/ir.model.access.csv'],

	'assets': {'web.assets_backend': ['ks_gantt_view_hr_holidays/static/src/js/ks_gantt_renderer_inherit.js']},
}

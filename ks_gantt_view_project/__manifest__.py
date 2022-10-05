# -*- coding: utf-8 -*-
{
	'name': 'Odoo Gantt View Project',

	'summary': """
Manage projects efficiently and perfectly with the unique application available in the market. Odoo Gantt View Project holds all the features to seamlessly modify the business. Gantt View Project, Gantt View, Gantt, Odoo Gantt View, Odoo Gantt, Web Gantt View, Odoo 14 community, Gantt Chart, Project Management, 
Planning view, Gantt Tasks, Odoo Web Gantt chart view, Odoo Project Web Gantt Chart View, All in one Odoo gantt view, Gantt Chart Project, Odoo Gantt Chart, Odoo Construction, Odoo Manufacturing, Gantt chart view, Project Web Gantt. Gantt View app is specifically designed to ease the tasks of project management. This platform provides a user-friendly Odoo interface with dynamic Gantt Native Web View to plan, manage, modify, and complete projects within a fixed timeline.
""",

	'description': """
odoo 15 project gantt view
        odoo 15 gantt view for project
        odoo 15 gantt chart
        odoo project gantt view
        gantt view in odoo
        project gantt view in odoo
""",

	'author': 'Ksolves India Ltd.',

	'license': 'OPL-1',

	'currency': 'EUR',

	'price': '24.9',

	'live_test_url': 'http://ganttview15.kappso.in/',

	'website': 'https://store.ksolves.com',

	'maintainer': 'Ksolves India Ltd.',

	'category': 'Tools',

	'version': '15.0.1.0.1',

	'support': 'sales@ksolves.com',

	'depends': ['ks_gantt_view_base', 'project', 'hr', 'hr_timesheet', 'hr_holidays'],

	'images': ['static/description/app_banner.jpg'],

	'data': ['data/ks_task_due_alert.xml', 'views/ks_gantt_task.xml', 'views/ks_gantt_project_views.xml', 'views/ks_project_task.xml', 'views/ks_project_all_task.xml', 'views/ks_gantt_import_wizard.xml', 'reports/ks_tasks_report.xml', 'reports/ks_timesheet_report.xml', 'security/ir.model.access.csv'],

	'assets': {'web.assets_backend': ['ks_gantt_view_project/static/src/js/ks_gantt_renderer_inherit.js', 'ks_gantt_view_project/static/src/js/ks_gantt_controller.js']},
}

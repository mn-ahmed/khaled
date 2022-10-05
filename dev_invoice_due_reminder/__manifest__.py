# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Invoice Due Date Reminder, Invoice due reminder',
    'version': '1.0',
    'sequence': 1,
    'category': 'Accounting',
    'description':
        """
 odoo app will send a mail to all invoice followers before two days and same day of invoice due date
        odoo Apps will send a mail to all invoice followers before two days and same day of invoice due date
Invoice due date reminder
Odoo invoice due date reminder
Due date reminder 
Odoo due date reminder
Customer invoice due date reminder
Odoo customer invoice due date reminder
Customer invoice due date reminder email
Odoo customer invoice due date reminder email
Send mail for invoice due date
Odoo send mail for invoice due date
Reminder on due date
Odoo reminder on due date
Odoo invoice reminder
Invoice reminder

odoo app will send a mail to all invoice followers before two days and same day of invoice due date, invocie reminder, due date reminder, invoice due date reminder, invoice reminder, customer invocie due reminder, invoice due date reminder, invoice customer reminder

    """,
    'summary': 'odoo app will send a mail to all invoice followers before two days and same day of invoice due date, invocie reminder, due date reminder, invoice due date reminder, invoice reminder, customer invocie due reminder, invoice due date reminder, invoice customer reminder',
    'author': 'Devintelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'depends': ['account'],
    'data': [
        'data/template_invoice_due_reminder.xml',
        'views/cron_invoice_due_reminder.xml',
        'views/dev_invoice_view.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price":12.0, 
    "currency":'EUR', 
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

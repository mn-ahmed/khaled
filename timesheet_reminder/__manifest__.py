# -*- coding: utf-8 -*-

{
    'name': 'Timesheet Reminder',
    'version': '1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
Timesheet email reminder

    """,
    'summary': 'remind employees weekly timesheet',
    'depends': ['hr_timesheet'],
    'data': [
        'data/mail_template.xml',
        'views/cron.xml',
        'views/employee_reminder.xml',
        ],
    'demo': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    
    'author': 'Ali Elgarhi',
    'website': '',    
   
   
    
}


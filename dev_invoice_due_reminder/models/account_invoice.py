# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from datetime import datetime

from odoo import models, fields, api, tools,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    skip_reminder = fields.Boolean('Skip Reminder')

    def get_diff_days(self, invoice):
        if invoice:
            cur_date = datetime.now().strftime("%Y-%m-%d")
            be_date = datetime.strptime(str(cur_date), '%Y-%m-%d')
            due_date = datetime.strptime(str(invoice.invoice_date_due), '%Y-%m-%d')
            return (due_date - be_date).days

    def get_follower_email(self):
        email_list = []
        all_emails = False
        if self.message_follower_ids:
            for follower in self.message_follower_ids:
                if follower.partner_id and follower.partner_id.email:
                    if follower.partner_id.email not in email_list:
                        email_list.append(follower.partner_id.email)
        if email_list:
            all_emails = ','.join(map(str, email_list))
        return all_emails

    def invoice_due_date_reminder(self):
        before_day_template_id = self.env.ref('dev_invoice_due_reminder.invoice_due_date_reminder')
        same_day_template_id = self.env.ref('dev_invoice_due_reminder.invoice_due_date_reminder_same_day')
    
        invoice_ids = self.search([('state', '=', 'posted'),
                                   ('invoice_date_due', '!=', False),
                                   ('move_type', '=', 'out_invoice'),
                                   ('payment_state', '!=', 'paid'),
                                   ('skip_reminder', '=', False),
                                   ])
        if before_day_template_id or same_day_template_id:
            if invoice_ids:
                for invoice in invoice_ids:
                    diff_days = invoice.get_diff_days(invoice)
                    if diff_days == 0 or diff_days == 2:
                        email = invoice.get_follower_email()
                        if email and diff_days == 2:
                            if before_day_template_id:
                                before_day_template_id.write({'email_to': email})
                                before_day_template_id.send_mail(invoice.id, True)
                        elif email and diff_days == 0:
                            if same_day_template_id:
                                same_day_template_id.write({'email_to': email})
                                same_day_template_id.send_mail(invoice.id, True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

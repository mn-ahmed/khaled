# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api ,_
from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta

from odoo.addons.base.models.ir_mail_server import MailDeliveryException
_logger = logging.getLogger(__name__)



class OnboardingEmployeeAppraisal(models.Model):
    _inherit = 'onboarding.proccess'

    @api.model
    def create(self, vals):
        res = super(OnboardingEmployeeAppraisal, self).create(vals)
        date_after_month = date.today() + relativedelta(months=1)
        evaluation_survey = self.env['survey.survey'].browse('1')
        questionnaire_survey = self.env['survey.survey'].browse('5')
        new_appraisal = self.env['hr.appraisal'].create({
            'emp_id': vals['employee_id'],
            'appraisal_deadline': date_after_month,
            'hr_manager': True,
            'hr_emp': True,
            'manager_survey_id': evaluation_survey.id,
            'emp_survey_id': questionnaire_survey.id
        })
        emp_manager = vals['employee_manager']
        new_appraisal.hr_manager_id = [(4, emp_manager)]
        print('new_appraisal', new_appraisal)
        return res


class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    check_manager_mail = fields.Boolean(string="manager Check Done", default=False, copy=False)
    check_employee_mail = fields.Boolean(string="employee Check Done", default=False, copy=False)
    manager_mail_date = fields.Date(string='manager Mail Date', compute='get_date_to_mail')
    employee_mail_date = fields.Date(string='employee Mail Date', compute='get_date_to_mail')
    manager_record_url = fields.Char(default=False, copy=False, compute='_action_manager_survey_url')
    emp_record_url = fields.Char(default=False, copy=False, compute='_action_manager_survey_url')

    def _action_manager_survey_url(self):
        manager_action_url = '%s/%s' % (
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            self.manager_survey_id.get_start_url())
        emp_action_url = '%s/%s' % (
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            self.emp_survey_id.get_start_url())

        print(manager_action_url)
        self.manager_record_url = manager_action_url
        self.emp_record_url = emp_action_url

    @api.model
    @api.depends('emp_id')
    def get_date_to_mail(self):
        for rec in self:
            # if rec.emp_id.hiring:
            rec.manager_mail_date= rec.emp_id.hiring + timedelta(days=69) #after 12 week from hiring date
            rec.employee_mail_date = rec.emp_id.hiring + relativedelta(months=1)
            # else:
    @api.model
    def cron_send_appraisal_mail(self):
        manager_survey = self.search([('check_manager_mail', '=', False)])
        employee_survey = self.search([('check_employee_mail', '=', False)])

        for rec_manager in manager_survey:
            try:
                if rec_manager.manager_mail_date and rec_manager.manager_mail_date == fields.Date.today():
                    template = self.env.ref('onboarding_employee_appraisal.mail_template_reminder_manager_survey')
                    self.env['mail.template'].browse(template.id).send_mail(rec_manager.id, force_send=True, raise_exception=True)

                else:
                    pass

            except MailDeliveryException as e:
                _logger.warning('MailDeliveryException while sending mail for %d. survey', rec_manager.emp_id)

        for rec_emp in employee_survey:
            try:
                if rec_emp.employee_mail_date and rec_emp.employee_mail_date == fields.Date.today():
                    template = self.env.ref('onboarding_employee_appraisal.mail_template_reminder_emp_survey')
                    self.env['mail.template'].browse(template.id).send_mail(rec_emp.id, force_send=True,raise_exception=True)

                else:
                    pass
            except MailDeliveryException as e:
                _logger.warning('MailDeliveryException while sending mail for %d. survey', rec_emp.emp_id)


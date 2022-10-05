# -*- coding: utf-8 -*-
import datetime
from odoo.exceptions import ValidationError, UserError

from odoo import models, fields, api

TICKET_PRIORITY = [
    ('0', 'All'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

class SlaOnboard(models.Model):
    _name = 'onboard.sla'
    _order = "name"
    _description = "Onboard SLA Policies"

    name = fields.Char('SLA Onboard Name', required=True, index=True)
    description = fields.Text('SLA Onboard Description')
    active = fields.Boolean('Active', default=True)
    priority = fields.Selection(
        TICKET_PRIORITY, string='Minimum Priority',
        default='0', required=True,
        help='Tickets under this priority will not be taken into account.')
    time_days = fields.Integer('Days', default=0, required=True,
                               help="Days to reach given stage based on ticket creation date")
    stage = fields.Selection([
        ('a', "IT Lead"),

        ('b', "ERP Admin"),
        ('c', "Finance"),
        ('e', "HR Admin"),
        ('f', "Done")
    ], default='a', string="Stage", required=True)
    next_stage = fields.Selection([
        ('a', "IT Lead"),

        ('b', "ERP Admin"),
        ('c', "Finance"),
        ('e', "HR Admin"),
        ('f', "Done")
    ], default='a', string="Next Stage", required=True)
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours',
                                           default=lambda self: self.env.user.company_id.resource_calendar_id)


class OnboardDeadline(models.Model):

    _inherit = 'onboarding.proccess'

    deadline = fields.Date(string='Deadline', compute='_compute_sla_onboard', store=True)
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    sla_id = fields.Many2one('onboard.sla', string='SLA Onboard', compute='_compute_sla_onboard', store=True)
    employee_project = fields.Many2one('project.project', string='Employee Project')
    task_id = fields.Many2one('project.task', 'Task', index=True)
    employee_manager = fields.Many2one('hr.employee', string='Employee Manager')
    employee_department = fields.Many2one('hr.department', string='Employee Department')

    @api.onchange('employee_project')
    def onchange_employee_project(self):
        # force domain on task when project is set
        if self.employee_project:
            if self.employee_project != self.task_id.project_id:
                # reset task when changing project
                self.task_id = False
            return {'domain': {
                'task_id': [('project_id', '=', self.employee_project.id)]
            }}

    @api.onchange('task_id')
    def onchange_task_id(self):
        if not self.employee_project:
            self.employee_project = self.task_id.project_id




    # @api.model
    # def create(self, vals):
    #     res = super(OnboardDeadline, self).create(vals)
    #     dom = [('stage', '=', self.state), ('priority', '<=', self.priority)]
    #     sla = ticket.env['onboard.sla'].search(dom, order="time_days", limit=1)
    #
    #     return res

    @api.depends('state', 'priority')
    def _compute_sla_onboard(self):
        # if not self.user_has_groups("helpdesk.group_use_sla"):
        #     return
        today = datetime.date.today()
        for ticket in self:
            dom = [('stage', '=', ticket.state), ('priority', '<=', ticket.priority)]
            sla = ticket.env['onboard.sla'].search(dom, order="time_days", limit=1)
            working_calendar = ticket.sla_id.resource_calendar_id
            if sla and ticket.sla_id != sla and ticket.create_date:
                ticket.sla_id = sla.id
                ticket_create_date = fields.Datetime.from_string(ticket.create_date)
                if sla.time_days > 0:
                    x = sla.time_days
                    ticket.deadline = today + datetime.timedelta(days=x)
                else:
                    ticket.deadline = ticket_create_date

            else:
                ticket.deadline = today

    @api.model
    def get_email_to(self):
        # user = self.env['res.users'].search(
        #     [('groups_id', '=', self.env.ref('embassy_letter.embassy_letter_approve_group').id)])
        user_group = self.env.ref("sla_onboard.onboard_deadline_mail_group")
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        return ",".join(email_list)

    @api.model
    def deadline_onboard_mail(self):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        records=self.search([
            ('state', '!=', 'f'),
            ('deadline', '<=', fields.Date.today())])
        for rec in records:
            if rec.deadline and rec.deadline == tomorrow and rec.state != 'f':
                template = self.env.ref('sla_onboard.mail_template_it_onboarding_deadline')
                self.get_email_to()
                self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True,
                                                                            raise_exception=True)
    # def deadline_onboard_mail(self):
    #     today = datetime.date.today()
    #     tomorrow = today + datetime.timedelta(days=1)
    #     for rec in self:
    #         if rec.deadline and rec.deadline > tomorrow:
    #             if rec.state == 'a':
    #                 template = self.env.ref('sla_onboard.mail_template_it_onboarding_deadline')
    #                 self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True, raise_exception=True)
    #
    #             if rec.state == 'b':
    #                 template = self.env.ref('sla_onboard.mail_template_onboarding_deadline_for_erp_admin')
    #                 self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True,
    #                                                                         raise_exception=True)
    #             if rec.state == 'c':
    #                 template = self.env.ref('sla_onboard.mail_template_onboarding_deadline_for_finance')
    #                 self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True, raise_exception=True)
    #
    #             if rec.state == 'e':
    #                 template = self.env.ref('sla_onboard.mail_template_onboarding_deadline_for_hr_admin')
    #                 self.env['mail.template'].browse(template.id).send_mail(rec.id, force_send=True, raise_exception=True)

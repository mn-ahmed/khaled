from datetime import time, datetime, timedelta
import base64
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import json

_logger = logging.getLogger(__name__)


class KsProjectTask(models.Model):
    _inherit = "project.task"

    def ks_default_start_date(self):
        return fields.Datetime.to_string(datetime.combine(fields.Datetime.now(), datetime.min.time()))

    def ks_default_end_datetime(self):
        return fields.Datetime.to_string(datetime.combine(fields.Datetime.now() + timedelta(days=1), datetime.min.time()))

    ks_start_datetime = fields.Datetime("Start Date", required=True, default=ks_default_start_date)
    ks_end_datetime = fields.Datetime("End Date", required=True, default=ks_default_end_datetime)
    ks_color = fields.Char(string="Color", compute='ks_compute_color')
    ks_allow_subtask = fields.Boolean(related="project_id.allow_subtasks")
    ks_mark_important = fields.Boolean(string="Mark As Important", default=False, help="Mark as an important task")
    ks_work_duration = fields.Char(string="Duration", help="Working Duration in day Hours",
                                   compute='ks_compute_work_duration')
    ks_task_link_json = fields.Char(compute="ks_compute_json_data_task_link")
    ks_resource_hours_per_day = fields.Float(related='user_ids.employee_id.resource_calendar_id.hours_per_day')
    ks_resource_hours_available = fields.Char(compute='ks_compute_resource_hours_available')
    ks_task_link_ids = fields.One2many(
        comodel_name='ks.task.link',
        inverse_name='ks_source_task_id',
        string='Ks_task_link_ids')

    ks_schedule_mode = fields.Selection(
        string='Schedule Mode',
        selection=[('auto', 'Auto'),
                   ('manual', 'Manual')],
        default="manual")

    ks_constraint_task_type = fields.Selection(
        string='Constraint Type',
        selection=[('asap', 'As Soon As Possible'),
                   ('alap', 'As Late As Possible'),
                   ('snet', 'Start No Earlier Than'),
                   ('snlt', 'Start No Late Than'),
                   ('fnet', 'Finish No Earlier Than'),
                   ('fnlt', 'Finish No Later Than'),
                   ('mso', 'Must Start On'),
                   ('mfo', 'Must Finish On'),
                   ],
        default="asap", required=True)

    ks_constraint_task_date = fields.Datetime(string="Constraint Date")
    ks_enable_task_duration = fields.Boolean(string="Enable Task Duration")
    ks_task_duration = fields.Integer(string="Duration")
    ks_task_unschedule = fields.Boolean(string="Unschedule", default=False)
    ks_task_type = fields.Selection(string='Task Type', selection=[('task', 'Task'), ('milestone', 'Milestone')],
                                    default='task', required=True)
    ks_user_ids = fields.Char(compute="ks_compute_ks_user_id", default=[])

    def ks_compute_ks_user_id(self):
        # lst = []
        for i in range(0,len(self)):
            ks_temp  = []
            if len(self[i].user_ids)>0:

                for x in range(0, len(self[i].user_ids)):
                    ks_temp.append([self[i].user_ids[x].id, self[i].user_ids[x].name])
                    self[i].ks_user_ids = ks_temp

                    # self[i].ks_user_ids.append(self[i].ks_user_ids)
            else:
                self[i].ks_user_ids = ks_temp


    # @api.onchange('user_ids')
    # def ks_user_idd(self):
    #     for i in self:
    #         self.user_ids = [(6,0,[self.user_ids.id])]

    @api.depends('stage_id')
    def ks_compute_color(self):
        for ks_task in self:
            if ks_task.stage_id and ks_task.stage_id.ks_stage_color:
                ks_task.ks_color = ks_task.stage_id.ks_stage_color
            else:
                ks_task.ks_color = '#7C7BAD'

    @api.onchange('ks_start_datetime', 'ks_end_datetime', 'ks_work_duration')
    def ks_compute_work_duration(self):
        for rec in self:
            rec.ks_work_duration = 0
            if rec.ks_end_datetime and rec.ks_start_datetime and rec.ks_task_type != 'milestone':
                if (rec.ks_end_datetime - rec.ks_start_datetime).days == 0:
                    rec.ks_work_duration = str(rec.ks_end_datetime - rec.ks_start_datetime) + " hours"
                else:
                    rec.ks_work_duration = str(rec.ks_end_datetime - rec.ks_start_datetime)
            if rec.ks_start_datetime and rec.ks_task_type == 'milestone':
                rec.ks_end_datetime = rec.ks_start_datetime

    def ks_compute_json_data_task_link(self):
        for rec in self:
            ks_task_link_json = []
            for task_link in rec.ks_task_link_ids:
                ks_task_link_json.append(
                    {
                        'id': task_link.id,
                        'source': task_link.ks_source_task_id.id,
                        'target': task_link.ks_target_task_id.id,
                        'type': task_link.ks_task_link_type,
                    }
                )
            rec.ks_task_link_json = json.dumps(ks_task_link_json)

    # @api.constrains('user_ids')
    # def ks_user_ids(self):
    #     for i in self:
    #         if self.user_ids:
    #             for x in range(0, len(self.user_ids)):
    #                 self.user_ids = [self.user_ids[x].id, self.user_ids[x].name]

    @api.model
    def create(self, values):
        res = super(KsProjectTask, self).create(values)

        # Update task end datetime if task duration is enabled.
        if res.ks_task_duration and res.ks_enable_task_duration:
            res.ks_end_datetime = res.ks_start_datetime + timedelta(days=res.ks_task_duration)

        # if the task is in the auto mode and constraint type is 'asap' then needs to change its date.
        if values.get('ks_schedule_mode') == 'auto' and values.get('ks_constraint_task_type') in ['asap', 'alap']:
            self.ks_auto_schedule_mode()
        self.ks_validate_constraint()

        # send email if task is assigned to the user.
        if 'user_ids' in values:
            res.ks_send_email_task_assigned()
        return res

    def write(self, values):
        res = super(KsProjectTask, self).write(values)
        for rec in self:
            if values.get('ks_schedule_mode') == 'auto' and self.ks_constraint_task_type in ['asap', 'alap']:
                self.ks_auto_schedule_mode()
            elif values.get('ks_start_datetime') or values.get('ks_end_datetime') or values.get('ks_task_link_ids'):
                # if dates or task link changed from backend then rescheduled its dependent tasks.
                for record in self.ks_task_link_ids:
                    if record.ks_target_task_id.ks_schedule_mode == 'auto' and \
                            record.ks_target_task_id.ks_constraint_task_type == 'asap':
                        record.ks_target_task_id.ks_auto_schedule_mode()

            if values.get('ks_constraint_task_type') or values.get('ks_constraint_task_date'):
                rec.ks_validate_constraint()

            # No need to calculate end date if only start datetime is changed.
            if (values.get('ks_task_duration') or values.get('ks_task_duration') == 0) and rec.ks_enable_task_duration\
                    and not values.get('ks_start_datetime'):
                rec.ks_end_datetime = rec.ks_start_datetime + timedelta(days=rec.ks_task_duration)

            # send email if task is assigned to the user.
            if 'user_ids' in values:
                rec.ks_send_email_task_assigned()
        return res

    def ks_validate_constraint(self):
        """
        Function to validate task constraint violation with task start date, end date and constraint date.
        """

        # for constraint type 'Start no earlier than' - the task should start on the constraint date or after it.
        if self.ks_constraint_task_type == 'snet' and not self.ks_constraint_task_date <= self.ks_start_datetime:
            raise ValidationError(_("Task should be start on the constraint date or after it."))

        # for constraint type 'Start no later than' – the task should start on the constraint date or before it.
        if self.ks_constraint_task_type == 'snlt' and not self.ks_constraint_task_date >= self.ks_start_datetime:
            raise ValidationError(_("Task should be start on the constraint date or before it."))

        # for constraint type 'Finish no earlier than' – the task should end on the constraint date or after it.
        if self.ks_constraint_task_type == 'fnet' and not self.ks_constraint_task_date <= self.ks_end_datetime:
            raise ValidationError(_("Task should be finish on the constraint date or after it."))

        # for constraint type 'Finish no later than' - the task should end on the constraint date or before it.
        if self.ks_constraint_task_type == 'fnlt' and not self.ks_constraint_task_date >= self.ks_end_datetime:
            raise ValidationError(_("Task should be finish on the constraint date or before it."))

        # for constraint type 'Must start on' – the task should start exactly on the constraint date.
        if self.ks_constraint_task_type == 'mso' and self.ks_constraint_task_date != self.ks_start_datetime:
            raise ValidationError(_("Task should start exactly on the constraint date."))

        # for constraint type 'Must finish on' – the task should start exactly on the constraint date.
        if self.ks_constraint_task_type == 'mfo' and self.ks_constraint_task_date != self.ks_end_datetime:
            raise ValidationError(_("Task should finish exactly on the constraint date."))

    def ks_auto_schedule_mode(self):
        """
        Function to calculate task start and end date for schedule task.
        :return:
        """
        if self.ks_schedule_mode == 'auto':

            task_link = self.env['ks.task.link'].search([('ks_target_task_id', '=', self.id),
                                                         ('ks_source_task_id.project_id', '=', self.project_id.id)])
            # find the if task is not linked with other task if not linked then change start date with the
            # project start date
            if not task_link:
                ks_duration = self.ks_end_datetime - self.ks_start_datetime
                if self.ks_constraint_task_type == 'asap':
                    if self.project_id.ks_project_start < self.ks_start_datetime:
                        self.ks_start_datetime = self.project_id.ks_project_start
                        self.ks_end_datetime = self.project_id.ks_project_start + ks_duration
                    else:
                        self.ks_end_datetime = self.project_id.ks_project_start + ks_duration
                        self.ks_start_datetime = self.project_id.ks_project_start

                if self.ks_constraint_task_type == 'alap':
                    ks_closest_task = False
                    for rec in self.ks_task_link_ids:
                        if rec.ks_source_task_id.id == self.id:
                            if not ks_closest_task or ks_closest_task > rec.ks_target_task_id.ks_start_datetime:
                                ks_closest_task = rec.ks_target_task_id.ks_start_datetime

                    if ks_closest_task:
                        self.ks_end_datetime = ks_closest_task
                        self.ks_start_datetime = self.ks_end_datetime - ks_duration
                    # self.ks_start_datetime = self.project_id.ks_project_end
                    # self.ks_end_datetime = self.project_id.ks_project_end + ks_duration

            # Current task is attached with other task (Finish to start) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "0":
                ks_duration = self.ks_end_datetime - self.ks_start_datetime
                if task_link.ks_source_task_id.ks_end_datetime < self.ks_start_datetime:
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_end_datetime
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_end_datetime + ks_duration
                else:
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_end_datetime + ks_duration
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_end_datetime

            # Current task is attached with other task (Start to start) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "1":
                ks_duration = self.ks_end_datetime - self.ks_start_datetime
                if task_link.ks_source_task_id.ks_start_datetime < self.ks_start_datetime:
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_start_datetime
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_start_datetime + ks_duration
                else:
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_start_datetime + ks_duration
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_start_datetime

            # Current task is attached with other task (Finish to finish) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "2":
                ks_duration = self.ks_end_datetime - self.ks_start_datetime
                if task_link.ks_source_task_id.ks_end_datetime < self.ks_start_datetime:
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_end_datetime - ks_duration
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_end_datetime
                else:
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_end_datetime
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_end_datetime - ks_duration

            # Current task is attached with other task (Start to finish) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "3":
                ks_duration = self.ks_end_datetime - self.ks_start_datetime
                if task_link.ks_source_task_id.ks_start_datetime < self.ks_end_datetime:
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_start_datetime - ks_duration
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_start_datetime
                else:
                    self.ks_end_datetime = task_link.ks_source_task_id.ks_start_datetime
                    self.ks_start_datetime = task_link.ks_source_task_id.ks_start_datetime - ks_duration

        for rec in self.ks_task_link_ids:
            if rec.ks_target_task_id.ks_schedule_mode == 'auto':
                rec.ks_target_task_id.ks_auto_schedule_mode()

    @api.constrains('ks_start_datetime', 'ks_end_datetime')
    def _validate_task_date(self):
        """
        Function to validation end date should not be smaller then the start date.
        """
        for rec in self:
            if rec.ks_end_datetime < rec.ks_start_datetime and rec.ks_task_type != 'milestone':
                raise ValidationError(_("Task end date cannot be smaller then the start date."))

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
        }

        return self.env.ref('ks_gantt_view_project.ks_gantt_tasks_report').report_action(self, data=data)

    def ks_action_send_email_tasks(self):
        if not self.project_id.ks_mail_timesheet_user:
            raise ValidationError(_("Please select the user before sending the mail from project setting"))
        template_obj = self.env['mail.mail']
        message_body = _("Hi %s, Timesheet report for task %s is attached please check it.") % \
                       (self.project_id.ks_mail_timesheet_user.name, self.name)

        template_data = {
            'subject': _('Task Progress'),
            'body_html': message_body,
            'email_from': self.env.user.email,
            'email_to': self.project_id.ks_mail_timesheet_user.email
        }
        template_id = template_obj.sudo().create(template_data)
        self.ks_fetch_timesheet_report(template_id)
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
        }
        try:
            template_id.sudo().send(raise_exception=True)
            notification['params'] = {
                'message': _('Email send successfully'),
                'sticky': False,
            }

        except MailDeliveryException as error:
            notification['params'] = {
                'message': _('Error when sending mail: %s') % (error.args[0]),
                'sticky': True,
            }

        return notification

    def ks_fetch_timesheet_report(self, mail_template):
        """
        Function to create timesheet pdf report and attached the report to mail.
        :param mail_template: mail model object
        """
        self.ensure_one()
        report_template = self.env.ref('ks_gantt_view_project.action_report_gantt_tasks_timesheet')
        report_name = self.name + _(' timesheet.pdf')

        # report data and its format
        result, format = report_template._render_qweb_pdf([self.id])
        result = base64.b64encode(result)

        attachment_ids = []
        attachment_obj = self.env['ir.attachment']

        attachment_data = {
            'name': report_name,
            'datas': result,
            'type': 'binary',
            'res_model': 'mail.message',
            'res_id': mail_template.id,
        }

        attachment_ids.append((4, attachment_obj.create(attachment_data).id))
        if attachment_ids:
            mail_template.sudo().write({'attachment_ids': attachment_ids})

    @api.onchange('ks_task_duration')
    def ks_compute_task_duration(self):
        for rec in self:
            if rec.ks_start_datetime:
                if not rec.ks_task_duration:
                    rec.ks_task_duration = 0
                rec.ks_end_datetime = rec.ks_start_datetime + timedelta(days=rec.ks_task_duration)

    @api.onchange('ks_start_datetime', 'ks_enable_task_duration')
    def ks_calculate_task_duration(self):
        for rec in self:
            rec.ks_task_duration = 0
            if rec.ks_end_datetime and rec.ks_start_datetime:
                rec.ks_task_duration = (rec.ks_end_datetime - rec.ks_start_datetime).days

    def ks_compute_resource_hours_available(self):
        for rec in self:
            resource_availability = {}
            if rec.user_ids and rec.user_ids.employee_id and rec.user_ids.employee_id.resource_calendar_id:
                for i in range(0, len(rec.user_ids)):
                    ks_working_calendar = rec.user_ids[i].employee_id.resource_calendar_id
                for ks_avail_hours in ks_working_calendar.attendance_ids:
                    if not resource_availability.get(int(ks_avail_hours.dayofweek)+1):
                        resource_availability[int(ks_avail_hours.dayofweek) + 1] = []
                    ks_temp_hours = ks_avail_hours.hour_from
                    while ks_temp_hours < ks_avail_hours.hour_to:
                        resource_availability[int(ks_avail_hours.dayofweek) + 1].append(ks_temp_hours)
                        ks_temp_hours += 1
            # rec.ks_resource_hours_available = resource_availability
            rec.ks_resource_hours_available = json.dumps(resource_availability)

    def ks_send_email_task_assigned(self):
        """
        Function to send the email to notify the user for the task assigned.
        :return:
        """
        template_obj = self.env['mail.mail']
        if len(self.user_ids):
            for i in range(0,len(self.user_ids)):
                message_body = _("Hi %s, Task : %s has been assigned to you.") % \
                               (self.user_ids[i].name, self.name)

                template_data = {
                    'subject': _('Task Assignment Mail'),
                    'body_html': message_body,
                    'email_from': self.env.user.email,
                    'email_to': self.user_ids[i].email
                }
                template_id = template_obj.sudo().create(template_data)

            try:
                template_id.sudo().send(raise_exception=True)
            except MailDeliveryException as error:
                _logger.error(_('Task Assignment mail unsuccessful with the error : %s') % error)

    @api.model
    def ks_update_task_sequence(self, data):
        for index in data:
            if data[index].get('id'):
                vals = dict()
                if 'parent_id' in data[index]:
                    if data[index].get('parent_id'):
                        vals['parent_id'] = data[index].get('parent_id')
                    else:
                        vals['parent_id'] = False
                if 'sequence' in data[index]:
                    vals['sequence'] = data[index].get('sequence')
                self.env['project.task'].search([('id', '=', data[index].get('id'))]).write(vals)
                _logger.info(_('Sequence Changed'))

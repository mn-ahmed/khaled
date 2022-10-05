from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
import pytz
import datetime
from pytz import timezone, UTC
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import logging
import json

_logger = logging.getLogger(__name__)


class KsGanttViewProject(models.Model):
    _inherit = 'project.project'

    ks_project_start = fields.Datetime(string="Start Date", default=lambda self: fields.Datetime.now(), required=True)
    ks_project_end = fields.Datetime(string="End Date",
                                     default=lambda self: fields.Datetime.now() + datetime.timedelta(days=7),
                                     required=True)
    ks_enable_project_deadline = fields.Boolean(string='Deadline',
                                                help="Enable/Disable Deadline of the tasks.", default=True)
    ks_enable_task_dynamic_text = fields.Boolean(string='Dynamic Text',
                                                 help="Enable/Disable Task Dynamic Text.", default=True)
    ks_enable_task_dynamic_progress = fields.Boolean(string='Dynamic Progress',
                                                     help="Enable/Disable Task Dynamic Progress.", default=True)
    ks_days_off = fields.Boolean(string='Days Off', help="Enable to remove off days from the gantt", default=False)
    ks_hide_date = fields.Boolean(string='Hide Holiday Day', help='Hide holidays on the gantt view', default=False)
    ks_days_off_selection = fields.Many2many('ks.week.days', string="Select Days")

    ks_enable_quickinfo_extension = fields.Boolean(string='Quick Info',
                                                   help="Enable/Disable Quick Info.", default=True)

    ks_tooltip_task_name = fields.Boolean(string='Name', default=True, help='Enable task name on tooltip')
    ks_tooltip_task_duration = fields.Boolean(string='Duration', default=True, help='Enable task duration on tooltip')
    ks_tooltip_task_start_date = fields.Boolean(string='Start Date', default=True,
                                                help='Enable task start date on tooltip')
    ks_tooltip_task_end_date = fields.Boolean(string='End Date', default=True, help='Enable task end date on tooltip')
    ks_tooltip_task_progress = fields.Boolean(string='Progress', default=True, help='Enable task progress on tooltip')
    ks_tooltip_task_deadline = fields.Boolean(string='Deadline', default=True, help='Enable task deadline on tooltip')
    ks_tooltip_task_stage = fields.Boolean(string='Stage', default=True, help='Enable task stage on tooltip')
    ks_tooltip_task_constraint_type = fields.Boolean(string='Constraint Type', default=True,
                                                     help='Enable task constraint type on tooltip')
    ks_tooltip_task_constraint_date = fields.Boolean(string='Constraint Date', default=True,
                                                     help='Enable task constraint date on tooltip')

    ks_mail_timesheet_user = fields.Many2one('res.partner', string="Mail user")

    ks_project_task_json = fields.Char(compute="ks_compute_json_data_project_task")
    ks_project_task_linking = fields.Char(compute="ks_compute_json_data_project_task_link")

    @api.model
    def ks_project_config(self, project_id):
        ks_tooltip_fields = ['ks_tooltip_task_name', 'ks_tooltip_task_duration', 'ks_tooltip_task_start_date',
                             'ks_tooltip_task_end_date', 'ks_tooltip_task_progress', 'ks_tooltip_task_stage',
                             'ks_tooltip_task_constraint_type', 'ks_tooltip_task_constraint_date',
                             'ks_tooltip_task_deadline']
        ks_project_obj = self.env['project.project'].browse(project_id)
        ks_project_config = {
            'ks_project_start': ks_project_obj.ks_project_start if ks_project_obj.ks_project_start else False,
            'ks_project_end': ks_project_obj.ks_project_end if ks_project_obj.ks_project_end else False,
            'ks_enable_project_deadline': ks_project_obj.ks_enable_project_deadline,
            'ks_enable_task_dynamic_text': ks_project_obj.ks_enable_task_dynamic_text,
            'ks_enable_task_dynamic_progress': ks_project_obj.ks_enable_task_dynamic_progress,
            'ks_days_off': ks_project_obj.ks_days_off,
            'ks_hide_date': ks_project_obj.ks_hide_date,
            'ks_enable_quickinfo_extension': ks_project_obj.ks_enable_quickinfo_extension,
            'ks_allow_subtasks': ks_project_obj.allow_subtasks,
        }

        ks_day_off_list = []
        if ks_project_obj.ks_days_off:
            for rec in ks_project_obj.ks_days_off_selection:
                ks_day_off_list.append(rec.ks_day_no)

        ks_project_config['ks_days_off_selection'] = ks_day_off_list

        ks_project_tooltip_config = {}
        for config_field in ks_tooltip_fields:
            ks_project_tooltip_config[config_field] = ks_project_obj[config_field]

        ks_project_config['ks_project_tooltip_config'] = ks_project_tooltip_config
        return ks_project_config

    @api.model
    def ks_task_due_alert(self):
        """
        Function to check the task due date if the task due date is in 7 days, 3 days, 1 days then send the mail to the
        owner for the task deadline.
        :return:
        """

        # Todo: add this functionality on the basis of the project this functionality is enabled then send the mail
        #  otherwise don't send the mail.

        ks_today_date = datetime.datetime.today().date()
        ks_all_project = self.search([])

        for ks_project in ks_all_project:
            ks_all_task = self.env['project.task'].search([('project_id', '=', ks_project.id)])
            for ks_task in ks_all_task:
                for i in range(0, len(ks_task.user_ids)):
                    if ks_task.date_deadline and ks_task.user_ids:
                        if ks_today_date < ks_task.date_deadline and (ks_task.date_deadline - ks_today_date).days in [7, 3,
                                                                                                                      1]:
                            # Sending email to the user to remind the deadline of the task.
                            template_obj = self.env['mail.mail']
                            message_body = _("Hi %s, This mail is to remind you %s have only %s days for the deadline.") % \
                                           (
                                               ks_task.user_ids[i].name, ks_task.name,
                                               (ks_today_date - ks_task.date_deadline).days)

                            template_data = {
                                'subject': _('Task Deadline Reminder Mail'),
                                'body_html': message_body,
                                'email_from': self.env.user.email,
                                'email_to': ks_task.user_ids[i].email
                            }
                            template_id = template_obj.sudo().create(template_data)
                            try:
                                template_id.sudo().send(raise_exception=True)
                                _logger.info(
                                    _('Task deadline reminder mail send successfully for task : (%s), user (%s)') % (
                                        ks_task.name, ks_task.user_ids[i].name))
                            except MailDeliveryException as error:
                                _logger.error(
                                    _(
                                        'Task deadline reminder mail unsuccessfully for task : (%s), user (%s) \n error '
                                        'log : %s') % (
                                        ks_task.name, ks_task.user_ids[i].name, error))

    @api.model
    def ks_public_holidays(self):
        ks_project_holiday = []
        ks_pub_hol = self.env['resource.calendar.leaves'].search([('resource_id', '=', False)])
        for ks_holiday in ks_pub_hol:
            ks_hol_datetime = ks_holiday.date_from
            while ks_hol_datetime <= ks_holiday.date_to:
                if ks_hol_datetime not in ks_project_holiday:
                    ks_project_holiday.append(ks_hol_datetime)
                ks_hol_datetime += datetime.timedelta(days=1)
        return ks_project_holiday

    def ks_compute_json_data_project_task(self):
        for rec in self:
            ks_project_task_json = []
            ks_all_task_obj = self.env['project.task'].search([('project_id', '=', rec.id)])
            for ks_task in ks_all_task_obj:
                for ks_user in range(0, len(ks_task.user_ids)):
                    ks_project_task_json.append(
                        {
                            'id': 'task_' + str(ks_task.id),
                            'ks_task_start_date': str(ks_task.ks_start_datetime),
                            'ks_task_end_date': str(ks_task.ks_end_datetime),
                            'ks_task_id': 'task_' + str(ks_task.id),
                            'ks_task_name': ks_task.name,
                            'ks_task_color': ks_task.ks_color,
                            'ks_task_model': 'project.task',
                            'parent_id': 'task_' + str(ks_task.parent_id.id) if ks_task.parent_id.id else False,
                            'project_id': [ks_task.project_id.id, ks_task.project_id.name],
                            'partner_id': [ks_task.partner_id.id, ks_task.partner_id.name],
                            'company_id': [ks_task.company_id.id, ks_task.company_id.name],
                            'mark_as_important': ks_task.priority,
                            'ks_enable_task_duration': ks_task.ks_enable_task_duration,
                            'deadline': str(ks_task.date_deadline) if ks_task.date_deadline else False,
                            'progress': ks_task.progress,
                            'ks_allow_subtask': ks_task.ks_allow_subtask,
                            'ks_allow_parent_task': ks_task.ks_allow_subtask,
                            'ks_schedule_mode': ks_task.ks_schedule_mode,
                            'constraint_type': ks_task.ks_constraint_task_type,
                            'constraint_date': str(ks_task.ks_constraint_task_date) if ks_task.ks_constraint_task_date else False,
                            'stage_id': [ks_task.stage_id.id, ks_task.stage_id.name],
                            'unscheduled': ks_task.ks_task_unschedule,
                            'ks_owner_task': [ks_task.user_ids[ks_user].id, ks_task.user_ids[ks_user].name] if ks_task.user_ids else False,
                            'resource_working_hours': ks_task.ks_resource_hours_per_day,
                            'type': ks_task.ks_task_type,
                            'ks_resource_hours_available': ks_task.ks_resource_hours_available,
                            'ks_task_link_json': ks_task.ks_task_link_json,
                        }
                    )
            rec.ks_project_task_json = json.dumps(ks_project_task_json)

    def ks_compute_json_data_project_task_link(self):
        for rec in self:
            ks_project_task_json = []
            ks_all_task_obj = self.env['project.task'].search([('project_id', '=', rec.id)])
            for ks_task in ks_all_task_obj:
                for ks_user in range(0,len(ks_task.user_ids)):
                    ks_project_task_json.append(
                        {
                            'id': 'task_' + str(ks_task.id),
                            'ks_task_start_date': str(ks_task.ks_start_datetime),
                            'ks_task_end_date': str(ks_task.ks_end_datetime),
                            'ks_task_id': 'task_' + str(ks_task.id),
                            'ks_task_name': ks_task.name,
                            'ks_task_color': ks_task.ks_color,
                            'ks_task_model': 'project.task',
                            'parent_id': 'task_' + str(ks_task.parent_id.id) if ks_task.parent_id.id else False,
                            'project_id': ks_task.project_id.id,
                            'mark_as_important': ks_task.priority,
                            'deadline': str(ks_task.date_deadline) if ks_task.date_deadline else False,
                            'progress': ks_task.progress,
                            'ks_allow_subtask': ks_task.ks_allow_subtask,
                            'ks_allow_parent_task': ks_task.ks_allow_subtask,
                            'ks_schedule_mode': ks_task.ks_schedule_mode,
                            'constraint_type': ks_task.ks_constraint_task_type,
                            'constraint_date': str(
                                ks_task.ks_constraint_task_date) if ks_task.ks_constraint_task_date else False,
                            'stage_id': [ks_task.stage_id.id, ks_task.stage_id.name],
                            'unscheduled': ks_task.ks_task_unschedule,
                            'ks_owner_task': [ks_task.user_ids[ks_user].id, ks_task.user_ids[ks_user].name] if ks_task.user_ids else False,
                            'resource_working_hours': ks_task.ks_resource_hours_per_day,
                            'type': ks_task.ks_task_type,
                            'ks_resource_hours_available': ks_task.ks_resource_hours_available,

                        }
                    )
            rec.ks_project_task_json = json.dumps(ks_project_task_json)

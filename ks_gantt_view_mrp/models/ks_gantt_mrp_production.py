import json
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import time, datetime, timedelta

_logger = logging.getLogger(__name__)


class KsMrpProduction(models.Model):
    _inherit = 'mrp.production'

    def ks_default_start_date(self):
        return fields.Datetime.to_string(datetime.combine(fields.Datetime.now(), datetime.min.time()))

    def ks_default_end_datetime(self):
        return fields.Datetime.to_string(
            datetime.combine(fields.Datetime.now() + timedelta(days=1), datetime.min.time()))

    ks_datetime_start = fields.Datetime("Start Date", required=True, default=ks_default_start_date)
    ks_datetime_end = fields.Datetime("End Date", required=True, default=ks_default_end_datetime)
    ks_task_unschedule = fields.Boolean(string="Unschedule", default=False)
    ks_work_duration = fields.Char(string="Duration", help="Working Duration in day Hours",
                                   compute='ks_compute_work_duration')

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
        required="True",
        default="asap")

    ks_constraint_task_date = fields.Datetime(string="Constraint Date")
    ks_enable_task_duration = fields.Boolean(string="Enable Order Duration")
    ks_task_duration = fields.Integer(string="Duration")
    ks_resource_hours_per_day = fields.Float(compute="_ks_compute_resource_hours", string="Resource Hours Per Day")
    ks_task_link_ids = fields.One2many(
        comodel_name='ks.task.link',
        inverse_name='ks_source_mrp_id',
        string='Task links')
    ks_task_link_json = fields.Char(compute="ks_compute_json_data_task_link")

    ks_schedule_mode = fields.Selection(
        string='Schedule Mode',
        selection=[('auto', 'Auto'),
                   ('manual', 'Manual')],
        default="manual")

    ks_resource_hours_available = fields.Char(compute='ks_compute_resource_hours_available')
    ks_stage_color = fields.Char(compute='ks_compute_task_color')

    def ks_compute_json_data_task_link(self):
        for rec in self:
            ks_task_link_json = []
            for task_link in rec.ks_task_link_ids:
                ks_task_link_json.append(
                    {
                        'id': task_link.id,
                        'source': task_link.ks_source_mrp_id.id,
                        'target': task_link.ks_target_mrp_id.id,
                        'type': task_link.ks_task_link_type,
                    }
                )
            rec.ks_task_link_json = json.dumps(ks_task_link_json)

    @api.onchange('ks_source_mrp_id', 'ks_datetime_end', 'ks_work_duration')
    def ks_compute_work_duration(self):
        for rec in self:
            rec.ks_work_duration = 0
            if rec.ks_datetime_end and rec.ks_datetime_start:
                if (rec.ks_datetime_end - rec.ks_datetime_start).days == 0:
                    rec.ks_work_duration = str(rec.ks_datetime_end - rec.ks_datetime_start) + " hours"
                else:
                    rec.ks_work_duration = str(rec.ks_datetime_end - rec.ks_datetime_start)

    @api.onchange('ks_task_duration')
    def ks_compute_task_duration(self):
        for rec in self:
            if rec.ks_datetime_start:
                if not rec.ks_task_duration:
                    rec.ks_task_duration = 0
                rec.ks_datetime_end = rec.ks_datetime_start + timedelta(days=rec.ks_task_duration)

    def ks_compute_resource_hours_available(self):
        for rec in self:
            resource_availability = {}
            if rec.user_id and rec.user_id.employee_id and rec.user_id.employee_id.resource_calendar_id:
                ks_working_calendar = rec.user_id.employee_id.resource_calendar_id
                for ks_avail_hours in ks_working_calendar.attendance_ids:
                    if not resource_availability.get(int(ks_avail_hours.dayofweek) + 1):
                        if int(ks_avail_hours.dayofweek) + 1 == 7:
                            resource_availability[0] = []
                        else:
                            resource_availability[int(ks_avail_hours.dayofweek) + 1] = []

                    ks_temp_hours = ks_avail_hours.hour_from
                    while ks_temp_hours < ks_avail_hours.hour_to:
                        if int(ks_avail_hours.dayofweek) + 1 == 7:
                            resource_availability[0].append(ks_temp_hours)
                        else:
                            resource_availability[int(ks_avail_hours.dayofweek) + 1].append(ks_temp_hours)
                        ks_temp_hours += 1
            rec.ks_resource_hours_available = json.dumps(resource_availability)

    def ks_compute_task_color(self):
        """
        Function to compute task color.
        :return:
        """
        ks_gantt_setting = self.env.ref('ks_gantt_view_mrp.ks_gantt_mrp_data_settings')
        for rec in self:
            ks_stage_color = self.env['ks.mrp.gantt.stage.color'].search(
                [('ks_state', '=', rec.state), ('ks_gantt_setting', '=', ks_gantt_setting.id)], limit=1)
            if ks_stage_color and ks_stage_color.ks_color:
                rec.ks_stage_color = ks_stage_color.ks_color
            else:
                rec.ks_stage_color = '#7C7BAD'

    @api.model
    def create(self, values):
        res = super(KsMrpProduction, self).create(values)

        # Update task end datetime if task duration is enabled.
        if res.ks_task_duration and res.ks_enable_task_duration:
            res.ks_datetime_end = res.ks_datetime_start + timedelta(days=res.ks_task_duration)

        # if the task is in the auto mode and constraint type is 'asap' then needs to change its date.
        if values.get('ks_schedule_mode') == 'auto' and values.get('ks_constraint_task_type') in ['asap', 'alap']:
            self.ks_auto_schedule_mode()
        self.ks_validate_constraint()

        return res

    def write(self, values):
        res = super(KsMrpProduction, self).write(values)
        for rec in self:
            if values.get('ks_schedule_mode') == 'auto' and self.ks_constraint_task_type in ['asap', 'alap']:
                self.ks_auto_schedule_mode()
            elif values.get('ks_datetime_start') or values.get('ks_datetime_end') or values.get('ks_task_link_ids'):
                # if dates or task link changed from backend then rescheduled its dependent tasks.
                for record in self.ks_task_link_ids:
                    if record.ks_target_mrp_id.ks_schedule_mode == 'auto' and \
                            record.ks_target_mrp_id.ks_constraint_task_type == 'asap':
                        record.ks_target_mrp_id.ks_auto_schedule_mode()

            if values.get('ks_constraint_task_type') or values.get('ks_constraint_task_date'):
                rec.ks_validate_constraint()

            # No need to calculate end date if only start datetime is changed.
            if (values.get('ks_task_duration') or values.get('ks_task_duration') == 0) and rec.ks_enable_task_duration \
                    and not values.get('ks_datetime_start'):
                rec.ks_datetime_end = rec.ks_datetime_start + timedelta(days=rec.ks_task_duration)

        return res

    def ks_auto_schedule_mode(self):
        """
        Function to calculate order start and end date for schedule record.
        :return:
        """
        if self.ks_schedule_mode == 'auto':

            task_link = self.env['ks.task.link'].search([('ks_target_mrp_id', '=', self.id)])
            # find the if task is not linked with other task if not linked then change start date with the
            # project start date
            if not task_link:
                ks_duration = self.ks_datetime_end - self.ks_datetime_start

                if self.ks_constraint_task_type == 'alap':
                    ks_closest_task = False
                    for rec in self.ks_task_link_ids:
                        if rec.ks_source_mrp_id.id == self.id:
                            if not ks_closest_task or ks_closest_task > rec.ks_target_mrp_id.ks_datetime_start:
                                ks_closest_task = rec.ks_target_mrp_id.ks_datetime_start

                    if ks_closest_task:
                        self.ks_datetime_end = ks_closest_task
                        self.ks_datetime_start = self.ks_datetime_end - ks_duration

            # Current task is attached with other task (Finish to start) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "0":
                ks_duration = self.ks_datetime_end - self.ks_datetime_start
                if task_link.ks_source_mrp_id.ks_datetime_end < self.ks_datetime_start:
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_end
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_end + ks_duration
                else:
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_end + ks_duration
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_end

            # Current task is attached with other task (Start to start) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "1":
                ks_duration = self.ks_datetime_end - self.ks_datetime_start
                if task_link.ks_source_mrp_id.ks_datetime_start < self.ks_datetime_start:
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_start
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_start + ks_duration
                else:
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_start + ks_duration
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_start

            # Current task is attached with other task (Finish to finish) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "2":
                ks_duration = self.ks_datetime_end - self.ks_datetime_start
                if task_link.ks_source_mrp_id.ks_datetime_end < self.ks_datetime_start:
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_end - ks_duration
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_end
                else:
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_end
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_end - ks_duration

            # Current task is attached with other task (Start to finish) as target.
            if len(task_link) == 1 and task_link.ks_task_link_type == "3":
                ks_duration = self.ks_datetime_end - self.ks_datetime_start
                if task_link.ks_source_mrp_id.ks_datetime_start < self.ks_datetime_end:
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_start - ks_duration
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_start
                else:
                    self.ks_datetime_end = task_link.ks_source_mrp_id.ks_datetime_start
                    self.ks_datetime_start = task_link.ks_source_mrp_id.ks_datetime_start - ks_duration

        for rec in self.ks_task_link_ids:
            if rec.ks_target_mrp_id.ks_schedule_mode == 'auto':
                rec.ks_target_mrp_id.ks_auto_schedule_mode()

    def ks_validate_constraint(self):
        """
        Function to validate task constraint violation with task start date, end date and constraint date.
        """

        # for constraint type 'Start no earlier than' - the task should start on the constraint date or after it.
        if self.ks_constraint_task_type == 'snet' and not self.ks_constraint_task_date <= self.ks_datetime_start:
            raise ValidationError(_("Order should be start on the constraint date or after it."))

        # for constraint type 'Start no later than' – the task should start on the constraint date or before it.
        if self.ks_constraint_task_type == 'snlt' and not self.ks_constraint_task_date >= self.ks_datetime_start:
            raise ValidationError(_("Order should be start on the constraint date or before it."))

        # for constraint type 'Finish no earlier than' – the task should end on the constraint date or after it.
        if self.ks_constraint_task_type == 'fnet' and not self.ks_constraint_task_date <= self.ks_datetime_end:
            raise ValidationError(_("Order should be finish on the constraint date or after it."))

        # for constraint type 'Finish no later than' - the task should end on the constraint date or before it.
        if self.ks_constraint_task_type == 'fnlt' and not self.ks_constraint_task_date >= self.ks_datetime_end:
            raise ValidationError(_("Order should be finish on the constraint date or before it."))

        # for constraint type 'Must start on' – the task should start exactly on the constraint date.
        if self.ks_constraint_task_type == 'mso' and self.ks_constraint_task_date != self.ks_datetime_start:
            raise ValidationError(_("Order should start exactly on the constraint date."))

        # for constraint type 'Must finish on' – the task should start exactly on the constraint date.
        if self.ks_constraint_task_type == 'mfo' and self.ks_constraint_task_date != self.ks_datetime_end:
            raise ValidationError(_("Order should finish exactly on the constraint date."))

    @api.onchange('ks_datetime_start', 'ks_enable_task_duration')
    def ks_calculate_task_duration(self):
        for rec in self:
            rec.ks_task_duration = 0
            if rec.ks_datetime_end and rec.ks_datetime_start:
                rec.ks_task_duration = (rec.ks_datetime_end - rec.ks_datetime_start).days

    def _ks_compute_resource_hours(self):
        for rec in self:
            rec.ks_resource_hours_per_day = 0
            if rec.user_id and rec.user_id.employee_id and rec.user_id.employee_id.resource_calendar_id:
                rec.ks_resource_hours_per_day = rec.user_id.employee_id.resource_calendar_id.hours_per_day

    @api.constrains('ks_datetime_start', 'ks_datetime_end')
    def _validate_task_date(self):
        """
        Function to validation end date should not be smaller then the start date.
        """
        for rec in self:
            if rec.ks_datetime_end < rec.ks_datetime_start:
                raise ValidationError(_("End date cannot be smaller then the start date."))


from odoo import api, fields, models
import json


class KsGanttHrLeave(models.Model):
    _inherit = 'hr.leave'

    ks_hr_leave_link_json = fields.Char(compute="ks_compute_json_data_leave_link")
    ks_leave_link_ids = fields.One2many(
        comodel_name='ks.task.link',
        inverse_name='ks_source_hr_leave_id',
        string='Leave gantt link')
    ks_stage_color = fields.Char(compute='ks_compute_task_color')
    ks_resource_hours_available = fields.Char(compute='ks_compute_resource_hours_available')

    def ks_compute_json_data_leave_link(self):
        for rec in self:
            ks_hr_leave_link_json = []
            for task_link in rec.ks_leave_link_ids:
                ks_hr_leave_link_json.append(
                    {
                        'id': task_link.id,
                        'source': task_link.ks_source_hr_leave_id.id,
                        'target': task_link.ks_target_hr_leave_id.id,
                        'type': task_link.ks_task_link_type,
                    }
                )
            rec.ks_hr_leave_link_json = json.dumps(ks_hr_leave_link_json)

    def ks_compute_task_color(self):
        """
        Function to compute task color.
        :return:
        """
        for rec in self:
            ks_stage_color = self.env['ks.holiday.gantt.stage.color'].search([('ks_state', '=', rec.state)], limit=1)
            if ks_stage_color and ks_stage_color.ks_color:
                rec.ks_stage_color = ks_stage_color.ks_color
            else:
                rec.ks_stage_color = '#7C7BAD'

    def ks_compute_resource_hours_available(self):
        for rec in self:
            resource_availability = {}
            if rec.employee_id and rec.employee_id.resource_calendar_id:
                ks_working_calendar = rec.employee_id.resource_calendar_id
                for ks_avail_hours in ks_working_calendar.attendance_ids:
                    if not resource_availability.get(int(ks_avail_hours.dayofweek)+1):
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

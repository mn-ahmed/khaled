# -*- coding: utf-8 -*-

from odoo.addons.web.controllers.main import ExcelExport
from odoo import http
from odoo.http import request, content_disposition


class KsGanttExport(ExcelExport):
    @http.route('/web/ksgantt/export/xlsx/', type='http', auth="user")
    def ks_gantt_export_excel(self, project_id):
        ks_fields = self.ks_gantt_export_field()
        ks_export_data = []

        # Check if project id is not available.
        if project_id != 'false':
            project_id = [project_id]
        else:
            project_id = [project.id for project in request.env['project.project'].search([])]

        for ks_project in project_id:
            ks_task_data = request.env['project.task'].search([('project_id', '=', int(ks_project))])
            for ks_task in ks_task_data:
                ks_row_list = []
                for ks_export_field in ks_fields:
                    if ks_task._fields.get(ks_export_field) and ks_task._fields.get(ks_export_field).type == 'many2one':
                        ks_row_list.append(ks_task[ks_export_field].display_name)
                    elif ks_task._fields.get(ks_export_field):
                        ks_row_list.append(ks_task[ks_export_field])
                ks_export_data.append(ks_row_list)
        response_data = self.from_data(ks_fields, ks_export_data)
        return request.make_response(response_data,
                                     headers=[('Content-Disposition',
                                               content_disposition(self.filename('project_project'))),
                                              ('Content-Type', self.content_type)])

    def ks_gantt_export_field(self):
        return [
            'name',
            'priority',
            'project_id',
            # 'user_id',
            'partner_id',
            # 'company_id',
            'stage_id',
            'date_deadline',
            'ks_task_unschedule',
            'ks_task_type',
            'ks_enable_task_duration',
            'ks_start_datetime',
            'ks_end_datetime',
            'ks_schedule_mode',
            'ks_constraint_task_type',
            'ks_constraint_task_date'
        ]


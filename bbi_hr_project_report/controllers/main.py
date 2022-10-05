from ast import literal_eval

from odoo import http
from odoo.http import content_disposition, request


class XLSXReportController(http.Controller):

    @http.route('/web/content/download/hr_project_report/<string:date_start>/<string:date_end>/<int:project>',
                type='http', csrf=False)
    def get_report_xlsx(self, date_start, date_end, project, **kw):
        project = request.env['project.project'].search([('id', '=', project)])
        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                     (
                         'Content-Disposition',
                         content_disposition('Project Sheet' + '.xlsx'))
                     ]
        )
        request.env['hr.project.report.wizard'].get_hr_project_report(
            response,
            date_start,
            date_end,
            project,
        )
        return response

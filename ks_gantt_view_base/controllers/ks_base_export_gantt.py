# -*- coding: utf-8 -*-

import json

from odoo.addons.web.controllers.main import ExcelExport
from odoo import http, _
from odoo.http import request, content_disposition


class KsBaseGanttExportBase(ExcelExport):
    @http.route('/web/ksganttbase/export/xlsx', type='http', auth="user")
    def ks_gantt_base_export_excel(self, ks_fields, ks_model_name, ks_domain, ks_context):
        file_name = self.ks_get_export_file_name()
        ks_domain = self.ks_validate_domain(ks_domain)
        ks_fields = json.loads(ks_fields)
        ks_context = json.loads(ks_context)
        ks_export_data = []

        ks_model_data = request.env[ks_model_name].with_context(ks_context).search(ks_domain)
        for ks_data in ks_model_data:
            ks_row_list = []
            for ks_export_field in ks_fields:
                if ks_data._fields[ks_export_field].type == 'many2one':
                    ks_column_data = False
                    if ks_data[ks_export_field].id:
                        ks_column_data = str(ks_data[ks_export_field].id) + ',' + ks_data[ks_export_field].display_name
                    ks_row_list.append(ks_column_data)
                else:
                    ks_row_list.append(ks_data[ks_export_field])
            ks_export_data.append(ks_row_list)
        response_data = self.from_data(ks_fields, ks_export_data)
        return request.make_response(response_data,
                                     headers=[('Content-Disposition',
                                               content_disposition(self.filename(file_name.get(ks_model_name)))),
                                              ('Content-Type', self.content_type)])

    def ks_get_export_file_name(self):
        """
        Function to return export file name.
        :return:
        """
        return {
            'hr.leave': _('Time Off'),
            'mrp.production': _('Manufacturing Orders'),
            'mrp.workorder': _('Work Orders')
        }

    def ks_validate_domain(self, ks_domain):
        if not ks_domain:
            return []
        else:
            ks_domain_list = json.loads(ks_domain)
            ks_return_list = []
            for ks_list in ks_domain_list:
                if type(ks_list) is list:
                    ks_return_list.append(tuple(ks_list))
                else:
                    ks_return_list.append(ks_list)
            return ks_return_list

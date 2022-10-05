# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request, serialize_exception
from odoo.tools import html_escape, pycompat
from odoo.addons.web.controllers.main import ExcelExport
from odoo.exceptions import UserError

import json
import re
import io
import datetime
try:
    import xlwt
except ImportError:
    xlwt = None


class CoAReportController(http.Controller):

    @http.route('/account_parent/<string:output_format>/<string:report_name>/<int:report_id>', type='http', auth='user')
    def coa_pdf_report(self, output_format, report_name, report_id=False, **kw):
        uid = request.session.uid
        coa = request.env['account.open.chart'].with_user(uid).browse(report_id)
        try:
            if output_format == 'pdf':
                response = request.make_response(
                    coa.with_context(active_id=report_id).get_pdf(report_id),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=coa_report.pdf;')
                    ]
                )
                # response.set_cookie('fileToken', token)
                return response
        except Exception as e:
            se = serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))

    @http.route('/account_parent/export/xls', type='http', auth='user')
    def coa_xls_report(self, data, **kw):
        print(kw,"kwkwkw")
        coa_data = json.loads(data)
        report_id = coa_data.get('wiz_id', [])
        report_obj = request.env['account.open.chart'].browse(report_id)
        user_context = report_obj._build_contexts()

        lines = report_obj.with_context(print_mode=True, output_format='xls').get_pdf_lines()
        user_context.update(report_obj.generate_report_context(user_context))
        show_initial_balance = user_context.get('show_initial_balance')
        row_data = report_obj.get_xls_title(user_context)


        if show_initial_balance:
            row_data.append(
                ['Code', 'Name', 'Type', 'Initial Balance', 'Debit', 'Credit', 'Ending Balance', 'Unfoldable'])
        else:
            row_data.append(['Code', 'Name', 'Type', 'Debit', 'Credit', 'Balance', 'Unfoldable'])
        for line in lines:
            level = line.get('level')
            unfoldable = line.get('unfoldable')
            code = line.get('code').rjust(2 * (int(level) + len(line.get('code'))))
            name = line.get('name')
            ac_type = line.get('ac_type')
            initial_balance = line.get('initial_balance')
            debit = line.get('debit')
            credit = line.get('credit')
            balance = line.get('balance')
            if show_initial_balance:
                balance = line.get('ending_balance')
                row_data.append([code, name, ac_type, initial_balance, debit, credit,
                                 balance, unfoldable])
            else:
                row_data.append([code, name, ac_type, debit, credit,
                                 balance, unfoldable])
        columns_headers = ['', '', 'Chart Of Accounts', '', '']
        rows = row_data
        return request.make_response(
            self.coa_format_data(columns_headers, rows),
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=coa_report.xls;')
            ],
            # cookies={'fileToken': token}
        )

    def coa_format_data(self, fields, rows):
        if len(rows) > 65535:
            raise UserError(_('There are too many rows (%s rows, limit: 65535) to export as Excel 97-2003 (.xls) format. Consider splitting the export.') % len(rows))

        workbook = xlwt.Workbook(style_compression=2)
        worksheet = workbook.add_sheet('Sheet 1')
        style = xlwt.easyxf('align: wrap yes')
        font = xlwt.Font()
        font.bold = True
        font.height = 300
        style.font = font

        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname, style)
            worksheet.col(i).width = 8000  # around 220 pixels

        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')

        for row_index, row in enumerate(rows):
            unfoldable = row[-1]
            row.pop(-1)

            for cell_index, cell_value in enumerate(row):
                cell_style = base_style

                if isinstance(cell_value, bytes) and not isinstance(cell_value, pycompat.string_types):
                    # because xls uses raw export, we can get a bytes object
                    # here. xlwt does not support bytes values in Python 3 ->
                    # assume this is base64 and decode to a string, if this
                    # fails note that you can't export
                    try:
                        cell_value = pycompat.to_text(cell_value)
                    except UnicodeDecodeError:
                        raise UserError(_("Binary fields can not be exported to Excel unless their content is base64-encoded. That does not seem to be the case for %s.") % fields[cell_index])
                if isinstance(cell_value, str):
                    cell_value = re.sub("\r", " ", pycompat.to_text(cell_value))
                    # Excel supports a maximum of 32767 characters in each cell:
                    cell_value = cell_value[:32767]
                elif isinstance(cell_value, datetime.datetime):
                    cell_style = datetime_style
                elif isinstance(cell_value, datetime.date):
                    cell_style = date_style
                font = xlwt.Font()
                font.bold = False
                cell_style.font = font
                if row_index + 1 in [2, 5]:
                    font = xlwt.Font()
                    font.bold = True
                    cell_style.font = font
                if unfoldable:
                    font.bold = True

                worksheet.write(row_index + 1, cell_index, cell_value, cell_style)

        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data

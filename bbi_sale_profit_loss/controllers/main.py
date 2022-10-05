from ast import literal_eval

from odoo import http
from odoo.http import content_disposition, request


class XLSXReportController(http.Controller):

    @http.route('/web/content/download/sale_order_profit_loss_wizard/<string:date_start>/<string:date_end>',
                type='http', csrf=False)
    def get_report_xlsx(self, date_start, date_end, **kw):
        company_ids = literal_eval(kw.get('company_ids', [0]))
        order_id = int(kw.get('order_id', 0))
        partner_id = int(kw.get('partner_id', 0))
        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                     (
                         'Content-Disposition',
                         content_disposition('Guaranteed Revenue Sheet' + '.xlsx'))
                     ]
        )
        request.env['sale.order.profit.loss.wizard'].get_sale_order_profit_loss_wizard_report(
            response,
            date_start,
            date_end,
            company_ids,
            order_id,
            partner_id,
        )
        return response

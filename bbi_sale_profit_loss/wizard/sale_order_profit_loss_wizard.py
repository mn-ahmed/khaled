import io
import math
from datetime import datetime

import xlsxwriter

from odoo import models, fields, api
from odoo.tools.float_utils import float_round


class SaleOrderProfitLossWizard(models.TransientModel):
    _name = 'sale.order.profit.loss.wizard'

    fiscal_year = fields.Many2one('account.fiscal.year', string='Fiscal Year', required=True)
    date_start = fields.Date(string="Start Date", compute='_compute_fiscal_year_start_date', store=True)
    date_end = fields.Date(string="End Date", compute='_compute_fiscal_year_start_date', store=True)
    company_ids = fields.Many2many('res.company', 'res_company_sale_ordr_report_rel', 'sale_order_report_id',
                                   'company_id',
                                   string='Companies', default=lambda self: self.env.company.ids)
    order_id = fields.Many2one('sale.order', 'sale order')
    partner_id = fields.Many2one('res.partner', 'Partner')

    @api.depends('fiscal_year')
    def _compute_fiscal_year_start_date(self):
        for rec in self:
            rec.date_start = False
            rec.date_end = False
            if rec.fiscal_year:
                if rec.fiscal_year.date_from:
                    rec.date_start = rec.fiscal_year.date_from
                if rec.fiscal_year.date_to:
                    rec.date_end = rec.fiscal_year.date_to

    def action_download_sale_order_profit_loss(self):
        company_ids = self.company_ids.ids if self.company_ids.ids else [0]
        order_id = self.order_id.id if self.order_id.id else 0
        partner_id = self.partner_id.id if self.partner_id.id else 0
        return {
            'type': "ir.actions.act_url",
            'target': "self",
            'url': "/web/content/download/sale_order_profit_loss_wizard/{date_start}/{date_end}?company_ids={company_ids}&order_id={order_id}&partner_id={partner_id}".format(
                date_start=str(self.date_start), date_end=str(self.date_end), company_ids=company_ids,
                order_id=order_id, partner_id=partner_id
            )
        }

    def get_invoiced_order_details(self, order):
        order_details_dict = {}
        analytic_cost = 0.0
        if order:
            analytics_obj = self.env['account.analytic.account'].search([('name', '=', order.name)])
            if analytics_obj:
                for analytic_obj in analytics_obj:
                    analytic_cost += analytic_obj.debit
            order_details_dict['name'] = "Actual " + order.name + " " + str(order.partner_id.name)
            order_details_dict['q1'] = 0
            order_details_dict['q2'] = 0
            order_details_dict['q3'] = 0
            order_details_dict['q4'] = 0
            total = 0.0
            if order.invoice_ids:
                for invoice in order.invoice_ids:
                    if invoice.invoice_date:
                        quarter = int((invoice.invoice_date.month - 1) / 3) + 1
                        order_details_dict['q' + str(quarter)] += invoice.amount_untaxed
                        total += invoice.amount_untaxed
            order_details_dict['total_revenue'] = total
            gp = round((total - analytic_cost) / total if total > 0 else 1, 2)
            order_details_dict['gp'] = gp
            order_details_dict['total'] = round(total, 2)
            order_details_dict['total_gp_value'] = round(total * order_details_dict['gp'], 2)
            order_details_dict['variance_text_style'] = None
            order_details_dict['variance_number_style'] = None
            order_details_dict['variance_gp_style'] = None
        return order_details_dict

    def get_order_details(self, order, variance_text_style, variance_number_style, variance_gp_style):
        order_details_list = []
        if order:
            order_details_dict = {}
            gp = round(
                (
                        order.amount_untaxed - order.project_cost) / order.amount_untaxed if order.amount_untaxed > 0 else 1,
                2)
            total = sum([line.total_butch_amount for line in order.project_payment_term_ids])
            order_details_dict['name'] = order.name + " " + str(order.partner_id.name)
            order_details_dict['total_revenue'] = order.amount_untaxed
            order_details_dict['gp'] = gp
            order_details_dict['q1'] = 0
            order_details_dict['q2'] = 0
            order_details_dict['q3'] = 0
            order_details_dict['q4'] = 0
            if order.project_payment_term_ids:
                i = 1
                for line in order.project_payment_term_ids:
                    order_details_dict['q' + str(i)] = line.total_butch_amount
                    i += 1
            order_details_dict['total'] = round(total, 2)
            order_details_dict['total_gp_value'] = round(total * order_details_dict['gp'], 2)
            order_details_dict['variance_text_style'] = None
            order_details_dict['variance_number_style'] = None
            order_details_dict['variance_gp_style'] = None
            order_details_list.append(order_details_dict)
            order_invoices_dict = self.get_invoiced_order_details(order)
            order_details_list.append(order_invoices_dict)
        variance_details_dict = {}
        variance_details_dict['name'] = "Variance " + order.name + " " + str(order.partner_id.name)
        variance_details_dict['total_revenue'] = order_details_list[0]['total_revenue'] - order_details_list[1][
            'total_revenue']
        variance_details_dict['gp'] = order_details_list[0]['gp'] - order_details_list[1]['gp']
        variance_details_dict['q1'] = order_details_list[0]['q1'] - order_details_list[1]['q1']
        variance_details_dict['q2'] = order_details_list[0]['q2'] - order_details_list[1]['q2']
        variance_details_dict['q3'] = order_details_list[0]['q3'] - order_details_list[1]['q3']
        variance_details_dict['q4'] = order_details_list[0]['q4'] - order_details_list[1]['q4']
        variance_details_dict['total'] = order_details_list[0]['total'] - order_details_list[1]['total']
        variance_details_dict['total_gp_value'] = order_details_list[0]['total_gp_value'] - order_details_list[1][
            'total_gp_value']
        variance_details_dict['variance_text_style'] = variance_text_style
        variance_details_dict['variance_number_style'] = variance_number_style
        variance_details_dict['variance_gp_style'] = variance_gp_style

        order_details_list.append(variance_details_dict)

        return order_details_list

    def get_sale_order_profit_loss_wizard_report(self, response, date_start, date_end, company_ids,
                                                 order_id,
                                                 partner_id, ):
        start_date = datetime.strptime(date_start, '%Y-%m-%d').strftime("%Y-%m-%d 00:00:00")
        end_date = datetime.strptime(date_end, '%Y-%m-%d').strftime("%Y-%m-%d 23:59:59")
        domain = []
        if start_date and end_date:
            domain += [
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
            ]
        if company_ids:
            domain += [
                ('company_id', 'in', company_ids),
            ]
        if order_id:
            domain += [
                ('id', '=', order_id),
            ]
        if partner_id:
            domain += [
                ('partner_id', '=', partner_id),
            ]

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'strings_to_formulas': False, })
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 16, 'bold': True, 'align': 'center'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': '#071f75', 'font_size': 14, 'color': 'white', 'bold': True,
             'left': 1,
             'bottom': 1,
             'right': 1, 'top': 1,
             'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'font_size': 12, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})

        number_style = workbook.add_format(
            {'font_name': 'Times', 'font_size': 12, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1,
             'align': 'center'})

        #####################################################################################
        variance_text_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': '#dac711', 'bold': True, 'font_size': 14, 'left': 1, 'bottom': 1,
             'right': 1, 'top': 1,
             'align': 'left'})
        variance_number_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': '#dac711', 'bold': True, 'font_size': 14, 'left': 1, 'bottom': 1,
             'right': 1, 'top': 1,
             'align': 'center'})
        gp_style = workbook.add_format(
            {'font_name': 'Times', 'font_size': 12, 'left': 1, 'bottom': 1, 'num_format': '00%',
             'right': 1, 'top': 1,
             'align': 'center'})
        variance_gp_style = workbook.add_format(
            {'font_name': 'Times', 'fg_color': '#dac711', 'bold': True, 'font_size': 14, 'left': 1, 'bottom': 1,
             'num_format': '00%',
             'right': 1, 'top': 1,
             'align': 'center'})

        sheet = workbook.add_worksheet(name='Guaranteed Revenue Sheet')
        sheet.set_default_row(25)
        sheet.set_column(0, 0, 50)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 5)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 10)
        sheet.set_column(7, 7, 25)
        sheet.set_column(8, 8, 25)
        sheet.merge_range('A1:I1', 'Guaranteed Revenue Sheet from ' + ' ' + date_start + ' ' + 'To' + str(date_end),
                          title_style)
        sheet.write(2, 0, 'Project/Opportunity', header_style)
        sheet.write(2, 1, 'Total Revenue LE', header_style)
        sheet.write(2, 2, 'GP %', header_style)  # total revent -projectcost/totalreve
        sheet.write(2, 3, 'Q1', header_style)
        sheet.write(2, 4, 'Q2', header_style)
        sheet.write(2, 5, 'Q3', header_style)
        sheet.write(2, 6, 'Q4', header_style)
        sheet.write(2, 7, 'TOTAL', header_style)
        sheet.write(2, 8, 'Total GP Value', header_style)
        row = 3
        number = 1
        sale_orders = self.env['sale.order'].search(domain, order='date_order ASC')
        if sale_orders:
            for order in sale_orders:
                results_list = self.get_order_details(order, variance_text_style, variance_number_style,
                                                      variance_gp_style)
                if results_list:
                    for result in results_list:
                        sheet.write(row, 0, result['name'],
                                    result['variance_text_style'] if result['variance_text_style'] else text_style)
                        sheet.write(row, 1, result['total_revenue'],
                                    result['variance_number_style'] if result[
                                        'variance_number_style'] else number_style)
                        sheet.write(row, 2, result['gp'], result['variance_gp_style'] if result[
                            'variance_gp_style'] else gp_style)
                        sheet.write(row, 3, result['q1'] if result['q1'] else 0,
                                    result['variance_number_style'] if result[
                                        'variance_number_style'] else number_style)
                        sheet.write(row, 4, result['q2'] if result['q2'] else 0,
                                    result['variance_number_style'] if result[
                                        'variance_number_style'] else number_style)
                        sheet.write(row, 5, result['q3'] if result['q3'] else 0,
                                    result['variance_number_style'] if result[
                                        'variance_number_style'] else number_style)
                        sheet.write(row, 6, result['q4'] if result['q4'] else 0,
                                    result['variance_number_style'] if result[
                                        'variance_number_style'] else number_style)
                        sheet.write(row, 7, result['total'], result['variance_number_style'] if result[
                            'variance_number_style'] else number_style)
                        sheet.write(row, 8, result['total_gp_value'], result['variance_number_style'] if result[
                            'variance_number_style'] else number_style)
                        row += 1
                        number += 1
                row += 1
                number += 1

        # sheet.merge_range('A' + str(row + 1) + ':D' + str(row + 1),
        #                   'الإجمالى',
        #                   header_style)
        # sheet.write(row, 4, sum(total_t), header_style)
        # sheet.write(row, 5, sum(total_shikara), header_style)
        # sheet.write(row, 6, 0, header_style)
        # sheet.write(row, 7, 0, header_style)
        # sheet.write(row, 8, 0, header_style)
        # sheet.write(row, 9, sum(total_sale_refund_amount), header_style)
        # sheet.write(row, 10, sum(total_sale_refund_amount), header_style)
        # sheet.write_formula(row, 11, '=SUM(L5:L' + str(row) + ')', header_style)
        # sheet.write_formula(row, 12, '=M' + str(row), header_style)
        workbook.close()
        output.seek(0)
        generated_file = response.stream.write(output.read())
        output.close()

        return generated_file

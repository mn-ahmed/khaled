# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    entry_month = fields.Char('Month', compute='_compute_month_year_quarter', store=True)
    entry_year = fields.Char('Year', compute='_compute_month_year_quarter', store=True)
    entry_quarter = fields.Char('Quarter', compute='_compute_month_year_quarter', store=True)
    customer_id = fields.Many2one('res.partner', compute='_compute_customer_id', store=True)
    supplier_id = fields.Many2one('res.partner', compute='_compute_supplier_id', store=True)

    contact_customer_id = fields.Many2one('res.partner', compute='_compute_contact_type', store=True)
    contact_supplier_id = fields.Many2one('res.partner', compute='_compute_contact_type', store=True)

    @api.depends('partner_id')
    def _compute_contact_type(self):
        for rec in self:
            rec.contact_customer_id = False
            rec.contact_supplier_id = False
            if rec.partner_id:
                if rec.partner_id.contact_type == 'customer':
                    rec.contact_customer_id = rec.partner_id
                if rec.partner_id.contact_type == 'supplier':
                    rec.contact_supplier_id = rec.partner_id
                if rec.partner_id.contact_type == 'both':
                    rec.contact_supplier_id = rec.partner_id
                    rec.contact_customer_id = rec.partner_id

    @api.depends('partner_id')
    def _compute_customer_id(self):
        for rec in self:
            rec.customer_id = False
            if rec.partner_id:
                if rec.partner_id.customer_rank >= 1:
                    rec.customer_id = rec.partner_id.id

    @api.depends('partner_id')
    def _compute_supplier_id(self):
        for rec in self:
            rec.supplier_id = False
            if rec.partner_id:
                if rec.partner_id.supplier_rank >= 1:
                    rec.supplier_id = rec.partner_id.id

    @api.depends('move_id', 'move_id.date', 'move_id.invoice_date', 'date')
    def _compute_month_year_quarter(self):
        for rec in self:
            rec.entry_month = False
            rec.entry_year = False
            rec.entry_quarter = False
            if rec.move_id:
                if rec.move_id.date:
                    invoice_month = rec.move_id.date.month
                    quarter = int((invoice_month - 1) / 3) + 1
                    if quarter == 1:
                        rec.entry_quarter = str(quarter) + " " + "First Quarter"
                    if quarter == 2:
                        rec.entry_quarter = str(quarter) + " " + "Second Quarter"
                    if quarter == 3:
                        rec.entry_quarter = str(quarter) + " " + "Third Quarter"
                    if quarter == 4:
                        rec.entry_quarter = str(quarter) + " " + "Fourth Quarter"
                    year = rec.move_id.date.year
                    month = False
                    if invoice_month == 1:
                        month = 'A'
                    if invoice_month == 2:
                        month = 'B'
                    if invoice_month == 3:
                        month = 'C'
                    if invoice_month == 4:
                        month = 'D'
                    if invoice_month == 5:
                        month = 'E'
                    if invoice_month == 6:
                        month = 'F'
                    if invoice_month == 7:
                        month = 'G'
                    if invoice_month == 8:
                        month = 'H'
                    if invoice_month == 9:
                        month = 'K'
                    if invoice_month == 10:
                        month = 'L'
                    if invoice_month == 11:
                        month = 'M'
                    if invoice_month == 12:
                        month = 'N'
                    month = str(month) + " " + rec.move_id.date.strftime("%B")
                    rec.entry_month = str(month) + " " + str(year)

                    rec.entry_year = str(year)
                elif rec.move_id.invoice_date:
                    invoice_month = rec.move_id.invoice_date.month
                    quarter = int((invoice_month - 1) / 3) + 1
                    if quarter == 1:
                        rec.entry_quarter = str(quarter) + " " + "First Quarter"
                    if quarter == 2:
                        rec.entry_quarter = str(quarter) + " " + "Second Quarter"
                    if quarter == 3:
                        rec.entry_quarter = str(quarter) + " " + "Third Quarter"
                    if quarter == 4:
                        rec.entry_quarter = str(quarter) + " " + "Fourth Quarter"
                    year = rec.move_id.invoice_date.year
                    month = False
                    if invoice_month == 1:
                        month = 'A'
                    if invoice_month == 2:
                        month = 'B'
                    if invoice_month == 3:
                        month = 'C'
                    if invoice_month == 4:
                        month = 'D'
                    if invoice_month == 5:
                        month = 'E'
                    if invoice_month == 6:
                        month = 'F'
                    if invoice_month == 7:
                        month = 'G'
                    if invoice_month == 8:
                        month = 'H'
                    if invoice_month == 9:
                        month = 'K'
                    if invoice_month == 10:
                        month = 'L'
                    if invoice_month == 11:
                        month = 'M'
                    if invoice_month == 12:
                        month = 'N'
                    month = str(month) + " " + rec.move_id.invoice_date.strftime("%B")
                    rec.entry_month = str(month) + " " + str(year)

                    rec.entry_year = str(year)
                else:
                    if rec.date:
                        date_month = rec.date.month
                        quarter = int((date_month - 1) / 3) + 1
                        if quarter == 1:
                            rec.entry_quarter = str(quarter) + " " + "First Quarter"
                        if quarter == 2:
                            rec.entry_quarter = str(quarter) + " " + "Second Quarter"
                        if quarter == 3:
                            rec.entry_quarter = str(quarter) + " " + "Third Quarter"
                        if quarter == 4:
                            rec.entry_quarter = str(quarter) + " " + "Fourth Quarter"
                        year = rec.date.year
                        month = False
                        if date_month == 1:
                            month = 'A'
                        if date_month == 2:
                            month = 'B'
                        if date_month == 3:
                            month = 'C'
                        if date_month == 4:
                            month = 'D'
                        if date_month == 5:
                            month = 'E'
                        if date_month == 6:
                            month = 'F'
                        if date_month == 7:
                            month = 'G'
                        if date_month == 8:
                            month = 'H'
                        if date_month == 9:
                            month = 'K'
                        if date_month == 10:
                            month = 'L'
                        if date_month == 11:
                            month = 'M'
                        if date_month == 12:
                            month = 'N'
                        month = str(month) + " " + rec.date.strftime("%B")
                        rec.entry_month = str(month) + " " + str(year)
                        rec.entry_year = str(year)

            else:
                if rec.date:
                    date_month = rec.date.month
                    quarter = int((date_month - 1) / 3) + 1
                    if quarter == 1:
                        rec.entry_quarter = str(quarter) + " " + "First Quarter"
                    if quarter == 2:
                        rec.entry_quarter = str(quarter) + " " + "Second Quarter"
                    if quarter == 3:
                        rec.entry_quarter = str(quarter) + " " + "Third Quarter"
                    if quarter == 4:
                        rec.entry_quarter = str(quarter) + " " + "Fourth Quarter"
                    year = rec.date.year
                    month = False
                    if date_month == 1:
                        month = 'A'
                    if date_month == 2:
                        month = 'B'
                    if date_month == 3:
                        month = 'C'
                    if date_month == 4:
                        month = 'D'
                    if date_month == 5:
                        month = 'E'
                    if date_month == 6:
                        month = 'F'
                    if date_month == 7:
                        month = 'G'
                    if date_month == 8:
                        month = 'H'
                    if date_month == 9:
                        month = 'K'
                    if date_month == 10:
                        month = 'L'
                    if date_month == 11:
                        month = 'M'
                    if date_month == 12:
                        month = 'N'
                    month = str(month) + " " + rec.date.strftime("%B")
                    rec.entry_month = str(month) + " " + str(year)
                    rec.entry_year = str(year)

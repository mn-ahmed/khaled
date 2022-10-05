# -*- coding: utf-8 -*-


from odoo import fields, models,api,_
from odoo.exceptions import UserError
from odoo.exceptions import Warning

class account_invoice_line(models.Model):
    _inherit ='account.move.line'
    

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1

        amount_currency = price_subtotal * sign

        if self.move_id.manual_currency_rate_active:
            if self.move_id.manual_currency_rate > 0:
                #currency_rate = self.company_id.currency_id.rate / self.move_id.manual_currency_rate
                currency_rate =  self.move_id.manual_currency_rate
                balance = amount_currency*currency_rate
            else:
                balance = currency._convert(amount_currency, company.currency_id, company,
                                            date or fields.Date.context_today(self))

        else:
            balance = currency._convert(amount_currency, company.currency_id, company,
                                        date or fields.Date.context_today(self))

        return {
            'amount_currency': amount_currency,
            'currency_id': currency.id,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
        }


    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for line in self:
            company = line.move_id.company_id
            if line.move_id.manual_currency_rate > 0:
                #currency_rate = line.company_id.currency_id.rate / line.move_id.manual_currency_rate
                currency_rate = line.move_id.manual_currency_rate
                balance = line.amount_currency*currency_rate
            else:
                balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
            line.debit = balance if balance > 0.0 else 0.0
            line.credit = -balance if balance < 0.0 else 0.0

            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())


    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            line.name = line._get_computed_name()
            line.account_id = line._get_computed_account()
            taxes = line._get_computed_taxes()
            if taxes and line.move_id.fiscal_position_id:
                taxes = line.move_id.fiscal_position_id.map_tax(taxes)
            line.tax_ids = taxes
            line.product_uom_id = line._get_computed_uom()
            line.price_unit = line._get_computed_price_unit()

            # price_unit and taxes may need to be adapted following Fiscal Position
            line._set_price_and_tax_after_fpos()

            # # Convert the unit price to the invoice's currency.
            company = line.move_id.company_id
            
            if line.move_id.manual_currency_rate_active:
                #currency_rate = line.move_id.manual_currency_rate/company.currency_id.rate
                currency_rate = line.move_id.manual_currency_rate
                if line.move_id.is_sale_document(include_receipts=True):
                    price_unit = line.product_id.lst_price
                elif line.move_id.is_purchase_document(include_receipts=True):
                    price_unit = line.product_id.standard_price
                else:
                    return 0.0
                manual_currency_rate = price_unit * currency_rate
                line.price_unit = manual_currency_rate



    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        ''' Recompute the 'price_unit' depending of the unit of measure. '''
        if self.display_type in ('line_section', 'line_note'):
            return
        taxes = self._get_computed_taxes()
        if taxes and self.move_id.fiscal_position_id:
            taxes = self.move_id.fiscal_position_id.map_tax(taxes)
        self.tax_ids = taxes
        self.price_unit = self._get_computed_price_unit()
        company = self.move_id.company_id

        if self.move_id.manual_currency_rate_active:
            #currency_rate = self.move_id.manual_currency_rate/company.currency_id.rate
            currency_rate = self.move_id.manual_currency_rate
            if self.move_id.is_sale_document(include_receipts=True):
                price_unit = self.product_id.lst_price
            elif self.move_id.is_purchase_document(include_receipts=True):
                price_unit = self.product_id.standard_price
            else:
                return 0.0
            manual_currency_rate = price_unit * currency_rate
            self.price_unit = manual_currency_rate
          
          
        
class account_invoice(models.Model):
    _inherit ='account.move'
    
    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    manual_currency_rate = fields.Float('Rate', digits=(12, 6))

 
    @api.constrains("manual_currency_rate")
    def _check_manual_currency_rate(self):
        for record in self:
            if record.manual_currency_rate_active:
                if record.manual_currency_rate == 0:
                    raise UserError(_('Exchange Rate Field is required , Please fill that.'))

    @api.onchange('manual_currency_rate_active', 'currency_id')
    def check_currency_id(self):
        if self.manual_currency_rate_active:
            if self.currency_id == self.company_id.currency_id:
                self.manual_currency_rate_active = False
                raise UserError(_('Company currency and invoice currency same, You can not added manual Exchange rate in same currency.'))




# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

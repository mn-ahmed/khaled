

from odoo import models, fields, api
from odoo.exceptions import Warning
from datetime import date, datetime


class TravelCurrency(models.Model):
    _name = 'hr.travel.currency'
    _rec_name = 'currency_id'
    _description = "Currency Defining for travelling"

    travel_request_id = fields.Many2one('hr.emp.travel.request')
    status = fields.Boolean(default=False)
    currency_id = fields.Many2one('res.currency')
    amount = fields.Monetary()
    company_currency_id = fields.Many2one(related='travel_request_id.currency_id', string="Company Currency")
    amount_company_currency = fields.Monetary(currency_field='company_currency_id')
    journal_id = fields.Many2one(string="Journal", comodel_name="account.journal",
                                 domain="[('type','in',['bank','cash'])]")
    account_id = fields.Many2one(string="Account", comodel_name="account.account")
    account_move_id = fields.Many2one('account.move', string="Journal Entry")

    @api.onchange('journal_id')
    def change_account(self):
        if self.journal_id:
            if self.journal_id.default_debit_account_id:
                self.account_id = self.journal_id.default_debit_account_id.id
            else:
                raise Warning("Please select the default accounts for the journal")

    #  journal Entry
    #@api.multi
    def journal_action(self):
        try:
            value = int(self.env['ir.config_parameter'].sudo().get_param('debit_account_id')) or False
            if value != False:
                move_line = []
                debit_acc_id = self.account_id
                lable_entry = self.travel_request_id.employee_id.name
                amount = self.amount
                credit_acc_id = value
                journal_id = self.journal_id
                company_currency = self.travel_request_id.currency_id
                current_currency = self.currency_id
                converted_amount = current_currency._convert(amount, company_currency, self.travel_request_id.company_id, date.today())
                move_line.append((0, 0, {'account_id': credit_acc_id,
                                         'name': lable_entry,
                                         'currency_id': current_currency.id,
                                         'amount_currency': 0 - amount,
                                         'credit': converted_amount,
                                         'debit': 0,
                                         'partner_id': self.travel_request_id.employee_id.user_id.partner_id.id,
                                         }))
                move_line.append((0, 0, {'account_id': debit_acc_id.id,
                                         'name': lable_entry,
                                         'currency_id': current_currency.id,
                                         'amount_currency': amount,
                                         'credit': 0,
                                         'debit': converted_amount,
                                         'partner_id': self.travel_request_id.employee_id.user_id.partner_id.id,
                                         }))
                move = {'journal_id': journal_id.id,
                        'ref': self.travel_request_id.name,
                        'line_ids': move_line,
                }
                move_id = self.env['account.move'].sudo().create(move)
                if move_id.id:
                    self.status = True
                    move_id.action_post()
                    self.amount_company_currency = converted_amount
                    self.account_move_id = move_id.id
                else:
                    raise Warning("Journal Entry is not done")
            else:
                raise Warning("Please Configure Account in the Employee Configuration")
        except Exception:
            raise Warning("Please Configure Account in the Employee Configuration")


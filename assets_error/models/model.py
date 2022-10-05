# -*- coding: utf-8 -*-


from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move','portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _description = "Journal Entry"
    _order = 'date desc, name desc, id desc'
    _mail_post_access = 'read'
    _check_company_auto = True
    _sequence_index = "journal_id"

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(_('You cannot create a move already in the posted state. Please create a draft move and post it after.'))

        vals_list = self._move_autocomplete_invoice_lines_create(vals_list)
        print(vals_list)
        update = {'partner_bank_id':False}
        new_dicts = [{**d, **update} for d in vals_list]
        print(new_dicts)
        return super(AccountMove, self).create(new_dicts)
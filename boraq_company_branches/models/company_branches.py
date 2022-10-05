from odoo import api, fields, models, tools, _
import base64
import os
import re
from odoo.exceptions import Warning

class CompanyBranches(models.Model):
    _name = "company.branches"
    _description="Company Branches"
    
    def write(self,vals):
        name_list = ['external_layout_background','external_layout_boxed','external_layout_clean','external_layout_standard']
        view_name = None
        if vals.get('external_report_layout_id',False):
            ir_ui_view_id = self.env['report.layout'].search([('view_id','=',vals.get('external_report_layout_id',False))],limit=1)
            view_name = ir_ui_view_id.view_id.name or False
            
        if view_name:
            if view_name in name_list:
                raise Warning('You cannot select, Please select anyone template from bellow')
        return super(CompanyBranches,self).write(vals)
    
    def _get_logo(self):
        return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_logo.png'), 'rb') .read())
    
    @api.model
    def _get_euro(self):
        return self.env['res.currency.rate'].search([('rate', '=', 1)], limit=1).currency_id

    @api.model
    def _get_user_currency(self):
        currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id
        return currency_id or self._get_euro()
    
    def change_report_template(self):
        self.ensure_one()
        template = self.env.ref('boraq_company_branches.view_branch_document_template_form')
        return {
            'name': _('Choose Your Document Layout'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'company.branches',
            'views': [(template.id, 'form')],
            'view_id': template.id,
            'target': 'new',
            'context':{'ctx_from_branch':True}
        }
        
    @api.model
    def _prepare_report_view_action(self, template):
        template_id = self.env.ref(template)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.ui.view',
            'view_mode': 'form',
            'res_id': template_id.id,
        }

    def edit_external_header(self):
        if not self.external_report_layout_id:
            return False
        return self._prepare_report_view_action(self.external_report_layout_id.key)
    
    name = fields.Char(string='Branch Name',required=True)
    country_id = fields.Many2one('res.country', string="Country")
    city = fields.Char(string="City")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    zip = fields.Char("Zip")
    state_id = fields.Many2one('res.country.state', string="State")
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    website = fields.Char("Website")
    vat = fields.Char(string="Tax ID")
    company_registry = fields.Char()
    logo = fields.Binary(default=_get_logo, string="Company Logo",)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self._get_user_currency())
    mobile = fields.Char("Mobile")
    external_report_layout_id = fields.Many2one('ir.ui.view', 'Document Template')
    report_header = fields.Text(string='Company Tagline', help="Appears by default on the top right corner of your printed documents (report header).")
    report_footer = fields.Text(string='Report Footer', translate=True, help="Footer text displayed at the bottom of all reports.")
    paperformat_id = fields.Many2one('report.paperformat', 'Paper format', default=lambda self: self.env.ref('base.paperformat_euro', raise_if_not_found=False))
    is_from_branch = fields.Boolean("From Branch",default=True)

    company_id = fields.Many2one("res.company","Company")
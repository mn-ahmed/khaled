# -*- coding: utf-8 -*-


from odoo import api, models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"
    
    def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
        account_template_account_dict = super(AccountChartTemplate, self).generate_account(tax_template_ref, acc_template_ref, code_digits, company)
        self.update_generated_account(tax_template_ref=tax_template_ref,code_digits=code_digits,
                                      company=company, importing_parent=True)
        return account_template_account_dict
    
    def update_generated_account(self, tax_template_ref=[], code_digits=1, company=False,importing_parent=False):
        """ This method for generating parent accounts from templates.

            :param tax_template_ref: Taxes templates reference for write taxes_id in account_account.
            :param code_digits: number of digits the accounts code should have in the COA
            :param company: company the wizard is running for
            :returns: return acc_template_ref for reference purpose.
            :rtype: dict
        """
        
        if not importing_parent:
            return True
        self.ensure_one()
        if not company:
            company = self.env.company
        if company.chart_template_id.id != self.id:
            return True
        
        account_tmpl_obj = self.env['account.account.template'].with_context({'show_parent_account':True})
        account_obj = self.env['account.account'].with_context({'show_parent_account':True})
        acc_templates = account_tmpl_obj.search([('nocreate', '!=', True), ('chart_template_id', '=', self.id),
                                                ], order='id')
        code_account_dict = {}
        
        for account_template in acc_templates:
            code_main = account_template.code and len(account_template.code) or 0
            code_acc = account_template.code or ''
            if code_main > 0 and code_main <= code_digits:
                code_acc =  str(code_acc) + (str('0'*(code_digits-code_main)))
            if account_template.user_type_id.type == 'view':
                new_code = account_template.code
            else:
                new_code = code_acc
            new_account = account_obj.search([('code', '=', new_code),
                                              ('company_id', '=', company.id)], limit=1)
            if not new_account:
                vals = self._get_account_vals(company, account_template, new_code, tax_template_ref)
                new_account_id = self.create_record_with_xmlid(company, account_template, 'account.account', vals)
                new_account = account_obj.browse(new_account_id)
            if new_code not in code_account_dict:
                code_account_dict[new_code] = new_account
        for code_prefix in ['bank_account_code_prefix', 'cash_account_code_prefix', 'transfer_account_code_prefix']:
            code_prefix_value = getattr(company, code_prefix, False)
            if code_prefix_value:
                if code_account_dict.get(code_prefix_value, False):
                    parent_account_id = code_account_dict.get(code_prefix_value, False)
                else:
                    parent_account_id = account_obj.search([
                        ('code', '=', code_prefix_value),
                        ('user_type_id.type', '=', 'view'),
                        ('company_id', '=', company.id)], limit=1)
                account = account_obj.search([('code', 'like', "%s%%"%code_prefix_value),
                                              ('id', '!=', parent_account_id.id),
                                              ('company_id', '=', company.id)])
                account and account.write({'parent_id': parent_account_id.id})
        ir_model_data = self.env['ir.model.data']
        for account_template in acc_templates:
            if not account_template.parent_id:
                continue
            template_xml_obj = ir_model_data.search([('model', '=', account_template._name), 
                                                     ('res_id', '=', account_template.id)])
            account_xml_id = "%s.%s_%s" % (template_xml_obj.module, company.id, template_xml_obj.name)
            account = self.env.ref(account_xml_id, raise_if_not_found=False)
            parent_template_xml_obj = ir_model_data.search([('model', '=', account_template._name), 
                                                            ('res_id', '=', account_template.parent_id.id)])
            parent_account_xml_id = "%s.%s_%s" % (parent_template_xml_obj.module, company.id, 
                                                  parent_template_xml_obj.name)
            parent_account = self.env.ref(parent_account_xml_id, raise_if_not_found=False)
            account.write({'parent_id': parent_account.id})
        return True
    

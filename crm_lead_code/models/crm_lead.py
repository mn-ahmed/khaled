##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class CrmLead(models.Model):
    _inherit = "crm.lead"

    code = fields.Char(string='Lead Number', required=True, default="/", readonly=False)

    opportunity_type = fields.Selection([('direct', 'Direct'), ('indirect', 'Indirect'), ('outsourcing', 'Outsourcing')]
                                        , string='Opportunity Type')
    user_ids = fields.Many2many('res.users', string="Unique Owners", compute='get_group_members')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', '/') == '/':
                vals['code'] = self.env['ir.sequence'].next_by_code('crm.lead')
        return super(CrmLead, self).create(vals_list)

    # @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('crm.lead')
        return super(CrmLead, self).copy(default)

    # @api.multi
    @api.onchange('opportunity_type')
    def get_group_members(self):
        for rec in self:
            if rec.opportunity_type:
                if rec.opportunity_type == 'direct':
                    users = self.env.ref('crm_lead_code.direct_manager_crm_group').users.ids
                    # rec.write({'user_ids': (6, 0, [users])})
                    rec.user_ids = [(6, 0, users)]
                    print(rec.user_ids)
                elif rec.opportunity_type == 'indirect':
                    users = self.env.ref('crm_lead_code.indirect_manager_crm_group').users.ids
                    # rec.write({'user_ids': (6, 0, [users])})
                    rec.user_ids = [(6, 0, users)]
                    print(rec.user_ids)

                elif rec.opportunity_type == 'outsourcing':
                    users = self.env.ref('crm_lead_code.outsource_manager_crm_group').users.ids
                    # rec.write({'user_ids': (6, 0, [users])})
                    rec.user_ids = [(6, 0, users)]
                    print(rec.user_ids)
            else:
                rec.user_ids = [(5, 0, 0)]



    # @api.multi
    def get_filtered_record(self):

        if self._context.get('params', False):
            params = self._context.get('params', False)
            if params.get('menu_id', False):
                raise ValidationError(
                    "Attention:You are not allowed to access this page due to Security Policy. In case of any query, please contact ERP Admin or Configuration Manager.")
        else:
            return False

        view_id_form = self.env['ir.ui.view'].search([('name', '=', 'crm.crm_case_form_view_oppor')])
        view_id_tree = self.env['ir.ui.view'].search([('name', '=', 'crm.crm_case_tree_view_oppor')])
        view_id_kanban = self.enf['ir.ui.view'].search([('name', '=', 'crm.crm_case_kanban_view_leads')])
        group_pool = self.env['res.groups']
        user = self.env['res.users'].browse(self._uid)
        employee_pool = self.env['hr.employee']
        employee = employee_pool.search([('user_id', '=', user.id)])
        if user.has_group('crm_lead_code.direct_manager_crm_group'):
            record_ids = self.env['crm.lead'].search([('opportunity_type', '=', 'direct')]).ids
        elif user.has_group('crm_lead_code.indirect_manager_crm_group'):
            record_ids = self.env['crm.lead'].search([('opportunity_type', '=', 'indirect')]).ids
        elif user.has_group('crm_lead_code.outsource_manager_crm_group'):
            record_ids = self.env['crm.lead'].search([('opportunity_type', '=', 'outsource')]).ids
        # else:
        #     record_ids = employee.ids
        return {
            'type': 'ir.actions.act_window',
            # 'name': _('Product'),
            'res_model': 'crm.lead',
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'view_id': view_id_tree.id,
            'views': [(view_id_tree.id, 'tree'), (view_id_form.id, 'form'), (view_id_kanban, 'kanban')],
            'target': 'current',
            'domain': [('id', 'in', record_ids)]
            # 'res_id': your.model.id,
        }

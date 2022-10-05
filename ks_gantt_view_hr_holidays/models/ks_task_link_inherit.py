from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class KsTaskLink(models.Model):
    _inherit = 'ks.task.link'

    ks_source_hr_leave_id = fields.Many2one(comodel_name='hr.leave', string="Source Task")
    ks_target_hr_leave_id = fields.Many2one(comodel_name='hr.leave', string='Target Task')

    # @api.onchange('ks_task_link_type')
    # def ks_compute_target_task_domain(self):
    #     ks_task_ids = []
    #     if self.ks_source_task_id and self.ks_source_task_id.project_id:
    #         ks_project_id = self.ks_source_task_id.project_id.id
    #         ks_task_ids = self.env['project.task'].sudo().search([('project_id', '=', ks_project_id)]).ids
    #     return {
    #         'domain': {
    #             'ks_target_task_id': [('id', '=', ks_task_ids)],
    #         }
    #     }

    @api.constrains('ks_source_hr_leave_id', 'ks_target_hr_leave_id')
    def ks_task_link_constraint(self):
        for rec in self:
            if rec.ks_source_hr_leave_id.id == rec.ks_target_hr_leave_id.id:
                raise ValidationError(_("Can't create same link with same task."))

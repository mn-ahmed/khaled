from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class KsTaskLink(models.Model):
    _inherit = 'ks.task.link'

    ks_source_mrp_id = fields.Many2one(comodel_name='mrp.production', string="Source Task")
    ks_target_mrp_id = fields.Many2one(comodel_name='mrp.production', string='Target Task')

    ks_source_wo_id = fields.Many2one(comodel_name='mrp.workorder', string='Source Task')
    ks_target_wo_id = fields.Many2one(comodel_name='mrp.workorder', string='Target Task')

    @api.constrains('ks_source_mrp_id', 'ks_target_mrp_id')
    def ks_task_link_constraint(self):
        """
        Linking check for manufacturing order.
        :return:
        """
        for rec in self:
            if rec.ks_source_mrp_id.id == rec.ks_target_mrp_id.id:
                raise ValidationError(_("Can't create same link with same record."))

    @api.constrains('ks_source_wo_id', 'ks_target_wo_id')
    def ks_task_link_constraint_wo(self):
        """
        Linking check for work orders.
        :return:
        """
        for rec in self:
            if rec.ks_source_wo_id.id == rec.ks_target_wo_id.id:
                raise ValidationError(_("Can't create same link with same record."))

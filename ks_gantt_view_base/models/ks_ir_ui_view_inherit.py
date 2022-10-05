from odoo import fields, models


# Inheriting view and adding Gantt view to View.
class KsGanttView(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(selection_add=[('ks_gantt', "Gantt")], ondelete={'ks_gantt': 'cascade'})

    def _postprocess_access_rights(self, node, model):
        # Model = self.env[model].sudo(False)
        is_base_model = self.env.context.get('base_model_name', model._name) == model._name
        if node.tag in 'ks_gantt':
            for action, operation in (('create', 'create'), ('delete', 'unlink'), ('edit', 'write')):
                if (not node.get(action) and
                        not model.check_access_rights(operation, raise_exception=False) or
                        not self._context.get(action, True) and is_base_model):
                    node.set(action, 'false')
        return super(KsGanttView, self)._postprocess_access_rights(node, model)

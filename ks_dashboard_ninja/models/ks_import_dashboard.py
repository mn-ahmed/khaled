import base64
import logging
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class KsDashboardNInjaImport(models.TransientModel):
    _name = 'ks_dashboard_ninja.import'
    _description = 'Import Dashboard'

    ks_import_dashboard = fields.Binary(string="Upload Dashboard", attachment=True)

    def ks_do_action(self):
        for rec in self:
            try:
                ks_result = base64.b64decode(rec.ks_import_dashboard)
                self.env['ks_dashboard_ninja.board'].ks_import_dashboard(ks_result)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
            except Exception as E:
                _logger.warning(E)
                raise ValidationError(_(E))

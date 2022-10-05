from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class KsGanttViewBaseImport(models.TransientModel):
    _inherit = 'ks.gantt.base.import.wizard'

    def ks_action_import_holiday(self):
        if self._context.get('ks_current_model') == 'hr.leave':
            if self.ks_file_type == 'xlsx':
                self.ks_import_xlsx_file('hr.leave')
            elif self.ks_file_type == 'json':
                ks_import_field = ["name", "holiday_status_id", "request_date_from", "request_date_to",
                                   "number_of_days", "date_from", "date_to", "holiday_type", "employee_id",
                                    "department_id", "request_date_from", "request_date_to"]
                self.ks_import_json_file('hr.leave', ks_import_field)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            return super()

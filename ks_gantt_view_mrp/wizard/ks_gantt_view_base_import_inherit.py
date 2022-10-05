from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class KsGanttViewBaseImport(models.TransientModel):
    _inherit = 'ks.gantt.base.import.wizard'

    def ks_action_import(self):
        if self._context.get('ks_current_model') in ['mrp.production', 'mrp.workorder']:
            if self.ks_file_type == 'xlsx':
                self.ks_import_xlsx_file(self._context.get('ks_current_model'))
            elif self.ks_file_type == 'json':
                ks_import_field = []
                if self._context.get('ks_current_model') == 'mrp.production':
                    ks_import_field = [
                        "name",
                        "product_id",
                        "product_qty",
                        "qty_producing",
                        "lot_producing_id",
                        "bom_id",
                        "date_planned_start",
                        "user_id",
                        "company_id",
                        "picking_type_id",
                        "origin",
                        "ks_task_unschedule",
                        "ks_enable_task_duration",
                        "ks_datetime_start",
                        "ks_datetime_end",
                        "ks_task_duration",
                        "ks_schedule_mode",
                        "ks_constraint_task_type",
                        "ks_constraint_task_date",
                        "state",
                        "product_uom_id"
                    ]
                if self._context.get('ks_current_model') == 'mrp.workorder':
                    ks_import_field = [
                        "production_id",
                        "date_planned_start",
                        "date_planned_finished",
                        "duration_expected",
                        "state",
                        "name",
                        "workcenter_id",
                        "product_uom_id",
                        "consumption"
                    ]
                self.ks_import_json_file(self._context.get('ks_current_model'), ks_import_field)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            return super()

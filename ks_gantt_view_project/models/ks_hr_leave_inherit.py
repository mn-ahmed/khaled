from odoo import api, fields, models
from datetime import timedelta


class KsHrLeave(models.Model):
    _inherit = 'hr.leave'

    def action_validate(self):
        result = super(KsHrLeave, self).action_validate()
        for rec in self:
            # Check if the leave is approved then increase the project task between the leave dates for the employee.
            if rec.state == 'validate':
                user_tasks = self.env['project.task'].search(
                    ['&', '|', '&', ('ks_start_datetime', '<=', rec.request_date_from),
                     ('ks_end_datetime', '>=', rec.request_date_from),
                     '&', ('ks_start_datetime', '<=', rec.request_date_to),
                     ('ks_end_datetime', '>=', rec.request_date_to),
                     ('user_ids', '=', rec.user_id.id)
                     ])

                for tasks in user_tasks:
                    tasks.ks_end_datetime += timedelta(days=int(rec.number_of_days))

        return result

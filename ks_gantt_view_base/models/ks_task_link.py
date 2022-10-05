from odoo import fields, models


class KsTaskLink(models.Model):
    _name = 'ks.task.link'
    _description = 'Ks Gantt Task Linking'

    ks_task_link_type = fields.Selection(
        string='Task Link Type',
        selection=[('0', 'Finish to start'),
                   ('1', 'Start to start'),
                   ('2', 'Finish to finish'),
                   ('3', 'Start to finish'),
                   ],
        required=True, )

    def unlink(self):
        """
        Override unlink function to avoid error 'could not serialize access due to concurrent update',
        this error occur when user tries to delete the record that is already deleted or not exist,
        problem with this - when this issue occurs then CRUD operations are also stopped working.
        """

        # Check if request id is already deleted or doesn't exist.
        for rec in self:
            try:
                if not len(self.env['ks.task.link'].search([('id', '=', rec.id)])):
                    return True
            except Exception as e:
                # If id is out of range.
                return True
        return super(KsTaskLink, self).unlink()


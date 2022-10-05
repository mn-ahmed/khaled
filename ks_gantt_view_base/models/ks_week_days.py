from odoo import fields, models


class KsWeekDays(models.Model):
    _name = 'ks.week.days'
    _description = 'Week Days'
    _rec_name = 'ks_day_name'

    ks_day_no = fields.Integer()
    ks_day_name = fields.Char(string='Day')

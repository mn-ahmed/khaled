# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import Warning


class leave_encash_report_wizard(models.TransientModel):
    _name = 'leave.encash.report.wizard'
    _description = 'Leave Encash Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    employee_ids = fields.Many2many("hr.employee", string="Employees")
    leave_type_ids = fields.Many2many("hr.leave.type", string="Leave Type")

    @api.onchange('end_date')
    def validate_date(self):
        if self.start_date > self.end_date:
            raise Warning(_("End Date Must Be Greater Than Start Date"))

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data = {'ids': self.ids,
                 'model': 'leave.encash.report.wizard',
                 'form': data
                 }
        return self.env.ref('flexi_hr.action_leave_encash_report').report_action(self, data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4

from collections import defaultdict
from lxml import etree
import re

from odoo import api, Command, fields, models, _
from datetime import date
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    def write(self, values):
        today = date.today()
        timeoff = 3
        for line in self:
         if line.task_id.id != timeoff:
           if line.date > today:
               raise AccessError(_("You cannot add timesheets next dates."))


# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
################################################################################


from  odoo import models, fields, api
from datetime import datetime
from collections import defaultdict, OrderedDict


class leave_encash_report(models.AbstractModel):
    _name = 'report.flexi_hr.leave_encash_report'
    _description = 'Report flexi hr  For Print Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('flexi_hr.leave_encash_report')
        return {
                'doc_ids': self.env['leave.encash.report.wizard'].browse(data['ids']),
                'doc_model': report.model,
                'docs': self,
                'data': data,
                'get_data': self.get_data,
                'get_total_encash': self.get_total_encash
                   }

    def get_data(self, data):
        if data.employee_ids:
            employe_ids = data.employee_ids.ids
        else:
            employe_ids = self.env['hr.employee'].search([]).ids
        if data.leave_type_ids:
          leave_type_ids = data.leave_type_ids.ids
        else:
            leave_type_ids = self.env['hr.leave.type'].search([]).ids
        query = """SELECT employee_id,
                    department_id,job_id,date,
                    leave_carry,amount,leave_type_id
                    from leave_encash where state = 'paid' and
                    date <= '%s' and
                    date >= '%s'
                    and employee_id in %s and leave_type_id in %s
                    Group by employee_id,department_id,job_id,date,
                    leave_carry,leave_type_id,amount""" % (data.end_date, data.start_date,
                                                         "(%s)" % ','.join(map(str, employe_ids)),
                                                         "(%s)" % ','.join(map(str, leave_type_ids)))
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        emp_dict = defaultdict(list)
        for each in results:
                emp_name = self.env['hr.employee'].browse(each['employee_id'])
                each.update({'employee_id': emp_name.name, 'department_id': emp_name.department_id.name
                             , 'job_id' : emp_name.job_id.name})
                leave_type = self.env['hr.leave.type'].browse(each['leave_type_id'])
                each.update({'leave_type_id' : leave_type.name})
                emp_dict[emp_name.name].append(each)
        final_dict = dict(emp_dict)
        return OrderedDict(sorted(final_dict.items(), key=lambda t: t[0]))

    def get_total_encash(self, data):
        if data.employee_ids:
            employe_ids = data.employee_ids.ids
        else:
            employe_ids = self.env['hr.employee'].search([]).ids
        if data.leave_type_ids:
          leave_type_ids = data.leave_type_ids.ids
        else:
            leave_type_ids = self.env['hr.leave.type'].search([]).ids
        query = """SELECT employee_id,
                    department_id,job_id,date,
                    leave_carry,amount,leave_type_id
                    from leave_encash where state = 'paid' and
                    date <= '%s' and
                    date >= '%s'
                    and employee_id in %s and leave_type_id in %s
                    Group by employee_id,department_id,job_id,date,
                    leave_carry,leave_type_id,amount""" % (data.end_date, data.start_date,
                                                        "(%s)" % ','.join(map(str, employe_ids)),
                                                        "(%s)" % ','.join(map(str, leave_type_ids)))
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        total_amount = 0
        for each in results:
            total_amount += each['amount']
        return total_amount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4

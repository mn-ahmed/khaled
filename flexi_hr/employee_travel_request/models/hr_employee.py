

from odoo import models, fields, api


class EmployeePublicInfo(models.Model):
    _inherit = 'hr.employee.public'

    grade_id = fields.Many2one('hr.emp.grade', string="Grade")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    grade_id = fields.Many2one('hr.emp.grade', string="Grade")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        if self.env.context.get('travel_request', False):
            hr_user = self.env.ref('hr.group_hr_manager')
            admin1 = self.env.ref('base.group_erp_manager')
            if not ((self.env.uid in hr_user.users.ids) or (self.env.uid in admin1.users.ids)):
                args += [('id', 'in', self.get_hirarchy())]
        return super(HrEmployee, self).name_search(name, args, operator, limit)

    #@api.multi
    def get_hirarchy(self):
        number = []
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        for emp in user_id.employee_ids:
            number.append(emp.id)
            val = emp.get_child_ids()
            if val:
                a = val.split('+')
                for num in a:
                    if num != '' and num != 'None':
                        number.append(int(num))
        return number

    #@api.multi
    def get_child_ids(self):
        if self.child_ids:
            lst = ""
            for each in self.child_ids:
                lst += str(each.id) + "+"
                lst += str(each.get_child_ids()) + "+"
        else:
            return
        return lst


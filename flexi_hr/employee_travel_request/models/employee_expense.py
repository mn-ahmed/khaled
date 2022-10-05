
from odoo import models, fields, api
from odoo.exceptions import Warning


class Grades(models.Model):
    _name = 'hr.emp.grade'
    _description = "different grades of employees"
    # _sql_constraints = [
    #     ('unique_grade', 'UNIQUE (name)', 'A grade must be unique!')
    # ]
    name = fields.Text(string="Grade", required="1")


class Expenses(models.Model):
    _name = 'hr.emp.expense'
    _description = "different names of expenses"

    name = fields.Text(string="Name")
    product_id = fields.Many2one('product.product',domain="[('can_be_expensed','=',True)]")
    exp_type = fields.Selection([('daily', 'Daily'), ('once', 'One Time')], string="Pay  For")


class ExpenseAmounts(models.Model):
    _name = 'hr.emp.expense.amount'
    _rec_name = 'expense_id'
    _description = "expenses and amount"

    grade_config_id = fields.Many2one('hr.emp.grade.config', store=True)
    expense_id = fields.Many2one('hr.emp.expense', string="Expense")

    exp_type = fields.Selection(related="expense_id.exp_type",store=True)
    product_id = fields.Many2one(related="expense_id.product_id", store=True)
    amount = fields.Monetary(string="Amount")
    currency_id = fields.Many2one(related="grade_config_id.currency_id", store=True)


class GradeExpenseConfigure(models.Model):
    _name = 'hr.emp.grade.config'
    _rec_name = 'grade_id'
    _description = "grade wise expenses"
    _sql_constraints = [
        ('unique_grade_id', 'UNIQUE (grade_id)', 'A grade must be unique!')
    ]
    grade_id = fields.Many2one('hr.emp.grade')
    expense_line_ids = fields.One2many('hr.emp.expense.amount', 'grade_config_id',string="Expenses")
    total = fields.Monetary(string="Total", compute="compute_total")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)

    #@api.multi
    def find_ids(self):
        values = []
        for rec in self.expense_line_ids:
            values.append(rec.expense_id.id)
        dupes = [x for n, x in enumerate(values) if x in values[:n]]
        if dupes:
            raise Warning("Please remove duplicate expenses.")

    # check duplicate values
    @api.constrains('expense_line_ids')
    def check_expense_line_ids(self):
        self.find_ids()

    @api.depends('expense_line_ids')
    def compute_total(self):
        for each in self:
            if each.expense_line_ids:
                each.total = sum([i.amount for i in each.expense_line_ids])
            else:
                each.total = None


class HrEmployeeExpenses(models.Model):
    _name = 'hr.expense.amount'
    _rec_name = 'expense_id'
    _description = "employee expenses and amount"

    travel_request_id = fields.Many2one('hr.emp.travel.request')
    expense_id = fields.Many2one('hr.emp.expense', string="Name")
    exp_type = fields.Selection(related="expense_id.exp_type", store="True", string="Type")
    product_id = fields.Many2one(related="expense_id.product_id", store="True")
    amount = fields.Monetary(string="Amount")
    approved_amount = fields.Monetary(string="Approved Amount")
    reason = fields.Text(string="Reason")
    total = fields.Monetary(compute="compute_amount_expense")
    currency_id = fields.Many2one(related="travel_request_id.currency_id", store=True)
    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")
    ], default='own_account',
        string="Process By")
    status = fields.Boolean(string="Status")

    # Calculate Total
    @api.depends('approved_amount')
    def compute_amount_expense(self):
        for each in self:
            if each.travel_request_id.expect_travel_days:
                if each.exp_type == 'daily':
                    each.total = each.approved_amount * each.travel_request_id.expect_travel_days
                else:
                    each.total = each.approved_amount
            else:
                each.total = each.approved_amount

    #  Expenses Entry
    #@api.multi
    def hr_expense_action(self):
        self.check_before_transaction()
        values = {
         'name':self.expense_id.name,
         'reference':self.travel_request_id.name,
         'product_id':self.product_id.id,
         'payment_mode':self.payment_mode,
         'employee_id':self.travel_request_id.employee_id.id,
         'unit_amount':self.total,
         'quantity':1,
         'total_amount':self.total,
         'travel_request_id_ref':self.travel_request_id.id,
        }
        store = self.env['hr.expense'].sudo().create(values)
        if store.id:
            self.expense_id_ref = store.id
            self.status = True
            return
            {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    # basic validation
    def check_before_transaction(self):
        if self.travel_request_id.name:
            return
        else:
            raise Warning("Please Save the Travel Request.")


class HrExpense(models.Model):
    _inherit = "hr.expense"

    travel_request_id_ref = fields.Many2one('hr.emp.travel.request')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
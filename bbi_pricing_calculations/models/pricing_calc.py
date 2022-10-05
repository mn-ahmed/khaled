# -*- coding: utf-8 -*-

from odoo import models, fields, api

COMPLEXITY = [
    ('0', 'Normal'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),

]

STATE = [
    ('draft', 'Draft'),
    ('technical_team', 'Technical Team'),
    ('pm', 'PM'),
    ('presales', 'Presales'),
    ('salesperson', 'Salesperson'),
    ('approved', 'Approved'),
    ('quotation', 'Quotation'),

]


class PricingCalc(models.Model):
    _name = "pricing.calc"
    _rec_name = 'lead_id'

    state = fields.Selection(STATE, string='State', tracking=True)
    lead_id = fields.Many2one('crm.lead', string='Opportunity')
    partner_id = fields.Many2one('res.partner', string='Customer')
    project_name = fields.Char(string='Project Name')
    sale_order_number = fields.Char(string='Sale Order #')
    currency_id = fields.Many2one('res.currency', string='Pricing Currency')
    currency_rate = fields.Char(string='Currency Rate')
    # project_country = fields.Many2one('')
    proposed_complexity = fields.Selection(COMPLEXITY, string='Proposed Complexity', tracking=True)
    deadline = fields.Date('Deadline')
    request_date = fields.Date('Request Date')
    presales_id = fields.Many2one('res.users', string='Presales')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    project_manager_id = fields.Many2one('res.users', string='Project manager')
    assigned_team_id = fields.Many2many('res.users', string='Assigned Team')

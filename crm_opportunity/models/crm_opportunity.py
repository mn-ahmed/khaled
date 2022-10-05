# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmOpportunity(models.Model):
    _inherit = "crm.lead"

    sector_ids = fields.Many2many('crm.sector', string='Sector/Segment')
    products_ids = fields.Many2many('crm.products.technologies', string='Products/Technologies')
    expected_competitors_ids = fields.Many2many('crm.expected.competitors', string='Expected Competitors')
    services_ids = fields.Many2many('crm.services', string='Services')
    outsourcing_ids = fields.Many2many('crm.outsourcing', string='Outsourcing')
    date_submittal = fields.Datetime(string='Submittal Date')
    license = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='License')
    service = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Service')
    territory_id = fields.Many2one('res.country', string="Territory")
    area_id = fields.Many2one('res.country.state', string="Area", store=True)
    business_text = fields.Text(string="Business/Technical Requirements (SOW)")

    vendor_id_new = fields.Many2one('res.partner', string='Vendor/Prim Contactor ')
    vendor_street = fields.Char('Vendor/Prim Street')
    vendor_street2 = fields.Char('Vendor/Prim Street2')
    vendor_zip = fields.Char('Vendor/Prim Zip', change_default=True)
    vendor_city = fields.Char('Vendor/Prim City')
    vendor_state_id = fields.Many2one("res.country.state", string='Vendor/Prim State')
    vendor_country_id = fields.Many2one('res.country', string='Vendor/Prim Country')
    vendor_website = fields.Char('Vendor/Prim Website', index=True, help="Website of the contact")
    vendor_contact_name = fields.Char('Vendor/Prim Contact Name',  track_sequence=3)
    vendor_phone = fields.Char('Vendor/Prim Phone')
    vendor_mobile = fields.Char('Vendor/Prim Mobile')
    vendor_function = fields.Char('Vendor/Prim Job Position')

    customer_id_new = fields.Many2one('res.partner', string='Customer(Partner/Reseller)')
    customer_street = fields.Char('Reseller Street')
    customer_street2 = fields.Char('Reseller Street2')
    customer_zip = fields.Char('Reseller Zip', change_default=True)
    customer_city = fields.Char('Reseller City')
    customer_state_id = fields.Many2one("res.country.state", string='Reseller State')
    customer_country_id = fields.Many2one('res.country', string='Reseller Country')
    customer_website = fields.Char('Reseller Website', index=True, help="Website of the contact")
    customer_contact_name = fields.Char('Reseller Contact Name', track_sequence=3)
    customer_phone = fields.Char('Reseller Phone')
    customer_mobile = fields.Char('Reseller Mobile')
    customer_function = fields.Char('Reseller Job Position')

    expected_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True,
                                      compute='_set_planned_revenue', store=True)
    probability = fields.Float('Probability', group_operator="avg", default=0.0, copy=False, compute='_set_probability', store=True)
    cost = fields.Integer('Cost', default=0 , compute='_set_cost', store=True)

    gp_percentage = fields.Float('GP Percentage', default=0, compute='_set_gp_percentage')
    gp_value = fields.Monetary('GP Value', currency_field='company_currency', compute='set_values_gp_value')
    value_odd = fields.Monetary('Value after Odd', currency_field='company_currency', compute='set_values_value_odd')
    gp_odd = fields.Monetary('GP after Odd', currency_field='company_currency', compute='set_values_gp_odd')

    is_outsourcing = fields.Boolean('Outsourcing', default=False)
    outsourcing_planned_revenue = fields.Monetary('Outsourcing Expected Revenue', currency_field='company_currency', tracking=True)
    outsourcing_probability = fields.Float('Outsourcing Probability', group_operator="avg", copy=False)
    outsourcing_value_odd = fields.Monetary('Outsourcing Value after Odd', currency_field='company_currency', compute='set_outsourcing_values_after_odd')
    outsourcing_cost = fields.Integer('Outsourcing Cost', default=0)

    outsourcing_gp_percentage = fields.Float('Outsourcing GP Percentage', compute='set_outsourcing_gp_percentage', store=True)
    outsourcing_gp_value = fields.Monetary('Outsourcing GP Value', currency_field='company_currency', compute='set_outsourcing_gp_value')
    outsourcing_gp_odd = fields.Monetary('Outsourcing GP after Odd', currency_field='company_currency', compute='set_outsourcing_gp_after_odd')

    is_services = fields.Boolean('Services', default=False)
    services_planned_revenue = fields.Monetary('Services Expected Revenue', currency_field='company_currency',tracking=True)
    services_probability = fields.Float('Services Probability', group_operator="avg", copy=False)
    services_value_odd = fields.Monetary('Services Value after Odd', currency_field='company_currency',
                                         compute='set_services_values_after_odd')
    services_cost = fields.Integer('Services Cost', default=0)

    services_gp_percentage = fields.Float('Services GP Percentage', compute='set_services_gp_percentage', store=True)
    services_gp_value = fields.Monetary('Services GP Value', currency_field='company_currency', compute='set_services_gp_value')
    services_gp_odd = fields.Monetary('Services GP after Odd', currency_field='company_currency',compute='set_services_gp_after_odd')

    is_license = fields.Boolean('License', default=False)
    license_planned_revenue = fields.Monetary('License Expected Revenue', currency_field='company_currency', tracking=True)
    license_probability = fields.Float('License Probability', group_operator="avg", copy=False)
    license_value_odd = fields.Monetary('License Value after Odd', currency_field='company_currency', compute='set_license_values_after_odd')
    license_gp_percentage = fields.Float('License GP Percentage',  compute='set_license_gp_percentage', store=True)
    license_cost = fields.Integer('License Cost', default=0)
    license_gp_value = fields.Monetary('License GP Value', currency_field='company_currency', compute='set_license_gp_value')
    license_gp_odd = fields.Monetary('License GP after Odd', currency_field='company_currency',compute='set_license_gp_after_odd')

    # @api.multi
    @api.depends('outsourcing_planned_revenue', 'services_planned_revenue', 'license_planned_revenue')
    def _set_planned_revenue(self):
        for rec in self:
            # if rec.outsourcing_planned_revenue or rec.services_planned_revenue or rec.license_planned_revenue:
            planned_revenue = rec.outsourcing_planned_revenue + rec.services_planned_revenue + rec.license_planned_revenue
            # print(planned_revenue)
            rec.expected_revenue = planned_revenue
            print(self.expected_revenue)

    # @api.multi
    @api.depends('outsourcing_cost', 'services_cost', 'license_cost')
    def _set_cost(self):
        for rec in self:
            # if rec.outsourcing_cost or rec.services_cost or rec.license_cost:
            cost = rec.outsourcing_cost + rec.services_cost + rec.license_cost
            rec.cost = cost


    # @api.multi
    @api.depends('outsourcing_probability', 'services_probability', 'license_probability')
    def _set_probability(self):
        x = 0
        y = 0
        z = 0
        if self.outsourcing_probability > 0:
            x = 1
        if self.services_probability > 0:
            y = 1
        if self.license_probability > 0:
            z = 1

        # if self.outsourcing_probability or self.services_probability or self.license_probability:
        try:
            probability = (self.outsourcing_probability + self.services_probability + self.license_probability)/(x+y+z)
        except ZeroDivisionError:
            probability = 0
        self.probability = round(probability, 1)

    # @api.multi
    @api.depends('outsourcing_gp_percentage', 'services_gp_percentage', 'license_gp_percentage')
    def _set_gp_percentage(self):
        x = 0
        y = 0
        z = 0
        for rec in self:
            if rec.outsourcing_gp_percentage > 0:
                x = 1
            if rec.services_gp_percentage > 0:
                y = 1
            if rec.license_gp_percentage > 0:
                z = 1

            # if rec.outsourcing_gp_percentage or rec.services_gp_percentage or rec.license_gp_percentage:
            try:
                gp_percentage = (rec.outsourcing_gp_percentage + rec.services_gp_percentage + rec.license_gp_percentage)/(x+y+z)
            except ZeroDivisionError:
                gp_percentage = 0
            rec.gp_percentage = round(gp_percentage, 1)

    @api.onchange('territory_id')
    def set_values_territory(self):
        if self.territory_id:
            ids = self.env['res.country.state'].search([('country_id', '=', self.territory_id.id)])
            return {
                'domain': {'area_id': [('id', 'in', ids.ids)], }
            }

    @api.onchange('vendor_country_id')
    def set_values_country_vendor(self):
        if self.vendor_country_id:
            ids = self.env['res.country.state'].search([('country_id', '=', self.vendor_country_id.id)])
            return {
                'domain': {'vendor_state_id': [('id', 'in', ids.ids)], }
            }

    # @api.multi
    @api.depends('gp_percentage','expected_revenue')
    def set_values_gp_value(self):
        for rec in self:
            # if rec.gp_percentage and rec.expected_revenue:
            rec.gp_value = (rec.expected_revenue * rec.gp_percentage)

    # @api.multi
    @api.depends('expected_revenue','probability')
    def set_values_value_odd(self):
        for rec in self:
            # if rec.expected_revenue and rec.probability:
            rec.value_odd = (rec.expected_revenue * rec.probability)/100


    # @api.multi
    @api.depends('probability', 'gp_value')
    def set_values_gp_odd(self):
        for rec in self:
            # if rec.probability and rec.gp_value:
            rec.gp_odd = (rec.gp_value * rec.probability) / 100

    # @api.multi
    @api.depends('outsourcing_planned_revenue', 'outsourcing_cost')
    def set_outsourcing_gp_percentage(self):
        for rec in self:
            # if rec.outsourcing_planned_revenue and rec.outsourcing_cost:
            try:
                outsourcing_gp_percentage = (rec.outsourcing_planned_revenue - rec.outsourcing_cost) / (rec.outsourcing_planned_revenue)
            except ZeroDivisionError:
                outsourcing_gp_percentage = 0
            rec.outsourcing_gp_percentage = outsourcing_gp_percentage
                # rec.outsourcing_gp_value = (rec.outsourcing_planned_revenue * rec.outsourcing_gp_percentage)/100


    # @api.multi
    @api.depends('services_planned_revenue', 'services_cost')
    def set_services_gp_percentage(self):
        for rec in self:
            # if rec.services_planned_revenue and rec.services_cost:
            if rec.services_planned_revenue != 0:
                services_gp_percentage = (rec.services_planned_revenue - rec.services_cost) / rec.services_planned_revenue
            else:
                services_gp_percentage = 0
            rec.services_gp_percentage = services_gp_percentage

    # @api.multi
    @api.depends('license_planned_revenue', 'license_cost')
    def set_license_gp_percentage(self):
        for rec in self:
            # if rec.license_planned_revenue and rec.license_cost:
            if rec.license_planned_revenue !=0:
                license_gp_percentage = (rec.license_planned_revenue - rec.license_cost) / rec.license_planned_revenue
            else:
                license_gp_percentage = 0
            rec.license_gp_percentage = license_gp_percentage


    # @api.multi
    @api.depends('outsourcing_planned_revenue', 'outsourcing_probability')
    def set_outsourcing_values_after_odd(self):
        for rec in self:
            # if rec.outsourcing_planned_revenue and rec.outsourcing_probability:
            outsourcing_value_odd = (rec.outsourcing_planned_revenue * rec.outsourcing_probability)/100
            rec.outsourcing_value_odd = round(outsourcing_value_odd,1)

    @api.depends('services_planned_revenue', 'services_probability')
    def set_services_values_after_odd(self):
        for rec in self:
            # if rec.services_planned_revenue and rec.services_probability:
            services_value_odd = (rec.services_planned_revenue * rec.services_probability) / 100
            rec.services_value_odd = round(services_value_odd, 1)

    @api.depends('license_planned_revenue', 'license_probability')
    def set_license_values_after_odd(self):
        for rec in self:
            # if rec.license_planned_revenue and rec.license_probability:
            license_value_odd = (rec.license_planned_revenue * rec.license_probability) / 100
            rec.license_value_odd = round(license_value_odd, 1)

    @api.depends('outsourcing_planned_revenue', 'outsourcing_gp_percentage')
    def set_outsourcing_gp_value(self):
        for rec in self:
            # if rec.outsourcing_gp_percentage and rec.outsourcing_planned_revenue:
            rec.outsourcing_gp_value = (rec.outsourcing_planned_revenue * rec.outsourcing_gp_percentage)

    @api.depends('services_planned_revenue', 'services_gp_percentage')
    def set_services_gp_value(self):
        for rec in self:
            # if rec.services_gp_percentage and rec.services_planned_revenue:
            rec.services_gp_value = (rec.services_planned_revenue * rec.services_gp_percentage)

    # @api.multi
    @api.depends('license_planned_revenue', 'license_gp_percentage')
    def set_license_gp_value(self):
        for rec in self:
            # if rec.license_gp_percentage and rec.license_planned_revenue:
            rec.license_gp_value = (rec.license_planned_revenue * rec.license_gp_percentage)

######

    @api.depends('outsourcing_probability', 'outsourcing_gp_value')
    def set_outsourcing_gp_after_odd(self):
        for rec in self:
            # if rec.outsourcing_probability and rec.outsourcing_gp_value:
            rec.outsourcing_gp_odd = (rec.outsourcing_probability * rec.outsourcing_gp_value) / 100

    @api.depends('services_probability', 'services_gp_value')
    def set_services_gp_after_odd(self):
        for rec in self:
            # if rec.services_probability and rec.services_gp_value:
            rec.services_gp_odd = rec.services_probability * rec.services_gp_value / 100

    # @api.multi
    @api.depends('license_probability', 'license_gp_value')
    def set_license_gp_after_odd(self):
        for rec in self:
            # if rec.license_probability and rec.license_gp_value:
            rec.license_gp_odd = rec.license_probability * rec.license_gp_value / 100


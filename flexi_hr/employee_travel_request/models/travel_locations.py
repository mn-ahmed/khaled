
from odoo import models, fields, api
from odoo.exceptions import Warning, _logger
from datetime import datetime


class TravelLocation(models.Model):
    _name = 'hr.emp.travel.location'
    _rec_name = 'dest_state_id'
    _description = "Travel Locations"

    travel_request_id_ref = fields.Many2one('hr.emp.travel.request')
    # travel_from
    source_street1 = fields.Char(string="From")
    source_street2 = fields.Char()
    source_state_id = fields.Many2one('res.country.state', string='State')
    source_country_id = fields.Many2one('res.country', string="Country")
    source_city = fields.Char()
    source_zip = fields.Integer()
    # travel_to
    dest_street1 = fields.Char(string="From")
    dest_street2 = fields.Char()
    dest_state_id = fields.Many2one('res.country.state', string='State')
    dest_country_id = fields.Many2one('res.country', string="Country")
    dest_city = fields.Char()
    dest_zip = fields.Integer()
    # travel Dates
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    # other details
    customer_id = fields.Many2one('res.partner', string="Customer")
    project_id = fields.Many2one('project.project', string="Customer")
    travel_days = fields.Integer(string="Days", compute="compute_days")
    reason = fields.Text(string="Reason")
    comment = fields.Text(string="Comment")

    # Days calculate
    @api.depends('start_date', 'end_date')
    def compute_days(self):
        for each in self:
            if each.start_date and each.end_date:
                d1 = datetime.strptime(str(each.end_date), '%Y-%m-%d')
                d2 = datetime.strptime(str(each.start_date), '%Y-%m-%d')
                daysDiff = (d1 - d2).days
                each.travel_days = int(daysDiff) + 1

    # country selection on state
    @api.onchange('dest_state_id')
    def onchange_dest_state_id(self):
        if self.dest_state_id:
            country = self.env['res.country.state'].search([('id', '=', self.dest_state_id.id)], limit=1)
            if country:
                self.dest_country_id = country.country_id

    @api.onchange('source_state_id')
    def onchange_source_state_id(self):
        if self.source_state_id:
            country = self.env['res.country.state'].search([('id', '=', self.source_state_id.id)], limit=1)
            if country:
                self.source_country_id = country.country_id

    # Date Validation
    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date:
            if (self.travel_request_id_ref.from_date > self.start_date) or (
                    self.travel_request_id_ref.to_date < self.start_date):
                raise Warning((
                        "Please Enter Dates Between " + str(self.travel_request_id_ref.from_date) + " and " + str(
                    self.travel_request_id_ref.to_date)))
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise Warning("Please Enter Valid From Date \n it must be less than To Date")

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date:
            if (self.travel_request_id_ref.from_date > self.end_date) or (
                    self.travel_request_id_ref.to_date < self.end_date):
                raise Warning(
                    "Please Enter Dates Between " + str(self.travel_request_id_ref.from_date) + " and " + str(self.travel_request_id_ref.to_date))
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise Warning("Please Enter Valid From Date \n it must be less than To Date")

    # constraints
    @api.constrains('start_date', 'end_date')
    def check_date(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise Warning("Please Enter Valid From Date \n it must be less than To Date")
            elif self.start_date < self.travel_request_id_ref.from_date or self.start_date > self.travel_request_id_ref.to_date:
                raise Warning("Please Check dates of Travel locations")
            elif self.end_date < self.travel_request_id_ref.from_date or self.end_date > self.travel_request_id_ref.to_date:
                raise Warning("Please Check dates of Travel locations")
        else:
            raise Warning("Please Enter Dates")


class TravelModes(models.Model):
    _name = 'hr.emp.travel.mode'
    _description = "Mode of Travelling"

    name = fields.Text(string="Mode")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
from odoo import models, fields, api


class SectorSegment(models.Model):
    _name = "crm.sector"
    _description = "Lead Sector"

    name = fields.Char('Name', required=True, translate=True)
    # color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Sector name already exists !"),
    ]


class ProductsTechnologies(models.Model):
    _name = "crm.products.technologies"
    _description = "Lead Products / Technologies"

    name = fields.Char('Name', required=True, translate=True)
    # color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Sector name already exists !"),
    ]


class ExpectedCompetitors(models.Model):
    _name = "crm.expected.competitors"
    _description = "Lead Expected Competitors"

    name = fields.Char('Name', required=True, translate=True)
    # color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Sector name already exists !"),
    ]


class CRMServices(models.Model):
    _name = "crm.services"
    _description = "Lead Services"

    name = fields.Char('Name', required=True, translate=True)
    # color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Sector name already exists !"),
    ]


class CRMOutsourcing(models.Model):
    _name = "crm.outsourcing"
    _description = "Lead Outsourcing"

    name = fields.Char('Name', required=True, translate=True)
    # color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Sector name already exists !"),
    ]
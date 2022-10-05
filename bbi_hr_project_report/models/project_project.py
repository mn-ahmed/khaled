# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning


class ProjectProject(models.Model):
    _inherit = "project.project"

    is_important = fields.Boolean(string='Is Important project')
    is_leave_project = fields.Boolean(string='Is Leave project')

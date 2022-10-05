# -*- coding: utf-8 -*-

from odoo import api, fields, models


class KsResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_gantt_theme = fields.Selection([('dhtmlxgantt_terrace.css', 'Default'),
                                       ('dhtmlxgantt_skyblue.css', 'Sky Blue'),
                                       ('dhtmlxgantt_meadow.css', 'Meadow'),
                                       ('dhtmlxgantt_broadway.css', 'Broadway'),
                                       ('dhtmlxgantt_material.css', 'Material'),
                                       ('dhtmlxgantt_contrast_white.css', 'Contrast White'),
                                       ('dhtmlxgantt_contrast_black.css', 'Contrast Black'),
                                       ], default='dhtmlxgantt_terrace.css', string='Gantt View Theme', required='True',
                                      config_parameter='ks_gantt_view_base.selected_theme')

    ks_gantt_rtl = fields.Boolean(string='Enable RTL', config_parameter='ks_gantt_view_base.ks_gantt_rtl',
                                  default=False)

    @api.model
    def ks_gantt_view_theme(self):
        ks_gantt_selected_theme = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'ks_gantt_view_base.selected_theme')], limit=1)

        ks_gantt_enable_rtl = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'ks_gantt_view_base.ks_gantt_rtl')], limit=1)

        return {'ks_gantt_view_theme': ks_gantt_selected_theme.value,
                'ks_gantt_rtl': ks_gantt_enable_rtl.value,
                }

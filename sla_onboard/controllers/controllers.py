# -*- coding: utf-8 -*-
from odoo import http

# class SlaOnboard(http.Controller):
#     @http.route('/sla_onboard/sla_onboard/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sla_onboard/sla_onboard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sla_onboard.listing', {
#             'root': '/sla_onboard/sla_onboard',
#             'objects': http.request.env['sla_onboard.sla_onboard'].search([]),
#         })

#     @http.route('/sla_onboard/sla_onboard/objects/<model("sla_onboard.sla_onboard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sla_onboard.object', {
#             'object': obj
#         })
# -*- coding: utf-8 -*-
from odoo import http

# class CrmOpportunity(http.Controller):
#     @http.route('/crm_opportunity/crm_opportunity/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_opportunity/crm_opportunity/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_opportunity.listing', {
#             'root': '/crm_opportunity/crm_opportunity',
#             'objects': http.request.env['crm_opportunity.crm_opportunity'].search([]),
#         })

#     @http.route('/crm_opportunity/crm_opportunity/objects/<model("crm_opportunity.crm_opportunity"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_opportunity.object', {
#             'object': obj
#         })
# -*- coding: utf-8 -*-
from odoo import http

# class EmbassyLetter(http.Controller):
#     @http.route('/embassy_letter/embassy_letter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/embassy_letter/embassy_letter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('embassy_letter.listing', {
#             'root': '/embassy_letter/embassy_letter',
#             'objects': http.request.env['embassy_letter.embassy_letter'].search([]),
#         })

#     @http.route('/embassy_letter/embassy_letter/objects/<model("embassy_letter.embassy_letter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('embassy_letter.object', {
#             'object': obj
#         })
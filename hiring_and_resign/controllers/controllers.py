# -*- coding: utf-8 -*-
from odoo import http

# class HiringAndResign(http.Controller):
#     @http.route('/hiring_and_resign/hiring_and_resign/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hiring_and_resign/hiring_and_resign/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hiring_and_resign.listing', {
#             'root': '/hiring_and_resign/hiring_and_resign',
#             'objects': http.request.env['hiring_and_resign.hiring_and_resign'].search([]),
#         })

#     @http.route('/hiring_and_resign/hiring_and_resign/objects/<model("hiring_and_resign.hiring_and_resign"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hiring_and_resign.object', {
#             'object': obj
#         })
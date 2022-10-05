# -*- coding: utf-8 -*-
from odoo import http

# class EmployeesInfo(http.Controller):
#     @http.route('/employees_info/employees_info/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employees_info/employees_info/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employees_info.listing', {
#             'root': '/employees_info/employees_info',
#             'objects': http.request.env['employees_info.employees_info'].search([]),
#         })

#     @http.route('/employees_info/employees_info/objects/<model("employees_info.employees_info"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employees_info.object', {
#             'object': obj
#         })
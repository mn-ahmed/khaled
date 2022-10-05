# -*- coding: utf-8 -*-
from odoo import http

# class OnboardingInfo(http.Controller):
#     @http.route('/onboarding_info/onboarding_info/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/onboarding_info/onboarding_info/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('onboarding_info.listing', {
#             'root': '/onboarding_info/onboarding_info',
#             'objects': http.request.env['onboarding_info.onboarding_info'].search([]),
#         })

#     @http.route('/onboarding_info/onboarding_info/objects/<model("onboarding_info.onboarding_info"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('onboarding_info.object', {
#             'object': obj
#         })
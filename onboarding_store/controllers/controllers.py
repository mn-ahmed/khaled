# -*- coding: utf-8 -*-
from odoo import http

# class OnboardingStore(http.Controller):
#     @http.route('/onboarding_store/onboarding_store/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/onboarding_store/onboarding_store/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('onboarding_store.listing', {
#             'root': '/onboarding_store/onboarding_store',
#             'objects': http.request.env['onboarding_store.onboarding_store'].search([]),
#         })

#     @http.route('/onboarding_store/onboarding_store/objects/<model("onboarding_store.onboarding_store"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('onboarding_store.object', {
#             'object': obj
#         })
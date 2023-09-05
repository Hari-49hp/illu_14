# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerSearch/(http.Controller):
#     @http.route('/partner_search//partner_search//', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_search//partner_search//objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_search/.listing', {
#             'root': '/partner_search//partner_search/',
#             'objects': http.request.env['partner_search/.partner_search/'].search([]),
#         })

#     @http.route('/partner_search//partner_search//objects/<model("partner_search/.partner_search/"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_search/.object', {
#             'object': obj
#         })

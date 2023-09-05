# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerCreditTransfer(http.Controller):
#     @http.route('/partner_credit_transfer/partner_credit_transfer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_credit_transfer/partner_credit_transfer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_credit_transfer.listing', {
#             'root': '/partner_credit_transfer/partner_credit_transfer',
#             'objects': http.request.env['partner_credit_transfer.partner_credit_transfer'].search([]),
#         })

#     @http.route('/partner_credit_transfer/partner_credit_transfer/objects/<model("partner_credit_transfer.partner_credit_transfer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_credit_transfer.object', {
#             'object': obj
#         })

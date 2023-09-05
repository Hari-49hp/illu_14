# -*- coding: utf-8 -*-
# from odoo import http


# class PptsNotification(http.Controller):
#     @http.route('/ppts_notification/ppts_notification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ppts_notification/ppts_notification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ppts_notification.listing', {
#             'root': '/ppts_notification/ppts_notification',
#             'objects': http.request.env['ppts_notification.ppts_notification'].search([]),
#         })

#     @http.route('/ppts_notification/ppts_notification/objects/<model("ppts_notification.ppts_notification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ppts_notification.object', {
#             'object': obj
#         })

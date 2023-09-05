# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, tools, _
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from datetime import datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale
import numpy as np

class CustomWebsiteSale(WebsiteSale):
    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, access_token=None, revive='', **post):
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                return request.render('website.404')
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        outstanding_amt = None
        if order.partner_id.total_due < 0:
            outstanding_amt = float(np.abs(order.partner_id.total_due))
        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
            'partner_outstanding_payment': outstanding_amt,
        })
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})
        return request.render("website_sale.cart", values)

    @http.route(['/shop/cart/adjust-advance'], type='http', auth="public", website=True, csrf=False)
    def adjust_advance(self, **post):
        if post['value_adjust_advance'] == 'True':
            order = request.website.sale_get_order();lines = [];line_id = [];line_product_price = '';line_product = '';ProductProduct = request.env['product.product']
            amount_adjst_flag=0.0
            product_id = 0
            if order.partner_id.total_due<0:
                amount_adjst_flag=(-1)
                product_id = ProductProduct.sudo().search([('default_code', '=', 'adjust-advance-code')])
                if not product_id:
                    product_id = ProductProduct.sudo().create({
                        'name': 'Adjust Advance',
                        'sale_ok': True,
                        'purchase_ok': False,
                        'lst_price': float(0),
                        'taxes_id': False,
                        'default_code': 'adjust-advance-code',
                    })
            else:
                amount_adjst_flag=1
                product_id = ProductProduct.sudo().search([('default_code', '=', 'adjust-dr-advance-code')])
                if not product_id:
                    product_id = ProductProduct.sudo().create({
                        'name': 'Adjust Debit Advance',
                        'sale_ok': True,
                        'purchase_ok': False,
                        'lst_price': float(0),
                        'taxes_id': False,
                        'default_code': 'adjust-dr-advance-code',
                    })


            for i in order.order_line:
                if i.product_id.default_code == 'adjust-advance-code' or i.product_id.default_code == 'adjust-dr-advance-code':
                    line_product = i
            if line_product:
                line_product_price = abs(line_product.price_unit) + float(post['adjust_advance'])
                line_product.write({
                    'price_unit':amount_adjst_flag*abs(line_product_price)
                    })
            else:
                lines.append((0, 0, {
                    'name' : product_id.name,
                    'product_id' : product_id.id,
                    'product_uom' : product_id.uom_id.id,
                    'product_uom_qty' : 1,
                    'price_unit':amount_adjst_flag*abs(float(post['adjust_advance'])),
                  }))
                order.write({ 'order_line' : lines })
            request.session['disc_outstanding_amt'] = float(post['adjust_advance'])
            return request.redirect('/shop/cart')

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        if order.partner_id.total_due < 0:
            amount_adjst_flag = (-1)
        else:
            amount_adjst_flag = 1

        if "disc_outstanding_amt" in request.session:
            for line in order.order_line:
                if line.product_id.default_code == 'adjust-advance-code'  or line.product_id.default_code == 'adjust-dr-advance-code':
                    line.price_unit = amount_adjst_flag*abs(float(request.session['disc_outstanding_amt']))
        return super(CustomWebsiteSale, self).checkout(**post)

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        order = request.website.sale_get_order()
        if order.partner_id.total_due < 0:
            amount_adjst_flag = (-1)
        else:
            amount_adjst_flag = 1

        if "disc_outstanding_amt" in request.session:
            for line in order.order_line:
                if line.product_id.default_code == 'adjust-advance-code'  or line.product_id.default_code == 'adjust-dr-advance-code':
                    line.price_unit = amount_adjst_flag*abs(float(request.session['disc_outstanding_amt']))
        return super(CustomWebsiteSale, self).payment(**post)


    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        order = request.env['sale.order'].browse(sale_order_id)
        if order:
            for line in order.order_line:
                if line.product_id.default_code == 'adjust-advance-code'  or line.product_id.default_code == 'adjust-dr-advance-code':
                    order.partner_id.total_due -= line.price_unit

        res = super(CustomWebsiteSale, self).payment_confirmation(**post)
        return res
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class SaleOrderLine(models.Model):   
    _inherit = "sale.order.line"
    
    order_ref = fields.Char('Order Reference',related='order_id.name')   
    customer_id = fields.Many2one('res.partner',related='order_id.partner_id')


class CouponProgram(models.Model):   
    _inherit = "coupon.program"

    @api.model
    def create(self, vals):
        program = super(CouponProgram, self).create(vals)
        if not vals.get('discount_line_product_id', False):
            discount_line_product_id = self.env['product.product'].create({
                'name': program.reward_id.display_name,
                'type': 'service',
                'taxes_id': False,
                'supplier_taxes_id': False,
                'sale_ok': True,
                'purchase_ok': False,
                'lst_price': 0,
                'invoice_policy': 'order',
            })
            program.write({'discount_line_product_id': discount_line_product_id.id})
        return program
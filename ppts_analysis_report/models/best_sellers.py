from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class BestSellersSummary(models.Model):
    _name = 'best.sellers.summary'
    _description="BestSellersSummary"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    product_id = fields.Many2one('product.product', string='Item Name')
    product_name = fields.Char(string='Item Full Name', related="product_id.name")
    color = fields.Char(string='Color')
    size = fields.Char(string='Size')
    qty = fields.Float(string='Quantity')
    total = fields.Monetary(currency_field='currency_id', string='Sales Total')
    pos_categ_id = fields.Many2one('pos.category', string='Category')
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),('product', 'Product')], string='Product Type')
    cogs = fields.Monetary(currency_field='currency_id',string='COGS')
    margin = fields.Char(string='Margin')
    pos_line_id = fields.Many2one('pos.order.line')
    pos_id = fields.Many2one('pos.order')
    date = fields.Date(string="Date")
    product_service = fields.Selection([
        ('consu', 'Consumable'),('product', 'Product'),
        ('service', 'Service')], string='Products/Services')


class BestSellersDetail(models.Model):
    _name = 'best.sellers.detail'
    _description="BestSellersDetail"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    product_id = fields.Many2one('product.product', string='Item Name')
    client = fields.Many2one('res.partner', string="Client")
    sale_id = fields.Many2one('pos.order')
    date = fields.Date(string='Sale Date', copy=False)
    pos_categ_id = fields.Many2one('pos.category', string='Category')
    qty = fields.Float(string='Quantity')
    color = fields.Char(string='Color')
    size = fields.Char(string='Size')
    total = fields.Monetary(currency_field='currency_id', string='Sales Total')
    product_service = fields.Selection(string='Products/Services', related='product_id.type')


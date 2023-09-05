from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class SalesByProduct(models.Model):
    _name = 'sales.product.summary'
    _description="SalesByProduct"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    product_id = fields.Many2one('product.product', string='Product Name')
    product_name = fields.Char(string='Product Full Name', related="product_id.name")
    pos_categ_id = fields.Many2one('pos.category', string='Category')
    color = fields.Char(string='Color')
    size = fields.Char(string='Size')
    barcode = fields.Char(string='Barcode')
    qty = fields.Float(string='Quantity')
    total = fields.Monetary(currency_field='currency_id',string='Total')
    cash_equal = fields.Monetary(currency_field='currency_id',string='Cash Equivalent')
    non_cash_equal = fields.Monetary(currency_field='currency_id',string='Non-Cash Equivalent')
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    pos_id = fields.Many2one('pos.order.line')
    date = fields.Date("Date")
    payment_method = fields.Selection([('cash', 'Cash'),('net', 'Net Banking'),
        ('bank', 'Bank')], string="Payment Method", default='cash')


class SalesByProductDetail(models.Model):
    _name = 'sales.product.detail'
    _description ="SalesByProductDetail"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    product_id = fields.Many2one('product.product', string='Product Name')
    product_name = fields.Char(string='Product Full Name', related="product_id.name")
    pos_categ_id = fields.Many2one('pos.category', string='Category', related="product_id.pos_categ_id")
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    pos_id = fields.Many2one('pos.order.line')
    client = fields.Many2one('res.partner', string="Client")
    client_id = fields.Char(string='Client ID')  # , related='client.sequence'
    sale_date = fields.Date(string='Sale Date', copy=False)
    unit_price = fields.Monetary(currency_field='currency_id',string="Unit Price")
    qty = fields.Float(string='Quantity')
    total = fields.Monetary(currency_field='currency_id', string='Total')
    cash_equal = fields.Monetary(currency_field='currency_id', string='Cash Equivalent')
    non_cash_equal = fields.Monetary(currency_field='currency_id', string='Non-Cash Equivalent', compute='compute_non_cash')
    payment_method = fields.Selection([('cash', 'Cash'),('net', 'Net Banking'),
        ('bank', 'Bank')], string="Payment Method", default='cash')


    def compute_non_cash(self):
        for rec in self:
            non = 0.00
            rec.non_cash_equal = rec.total - rec.cash_equal





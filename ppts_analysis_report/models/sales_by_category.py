from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class SalesByCategory(models.Model):
    _name = 'sales.category'
    _description="SalesByCategory"

    name = fields.Char()
    company_id = fields.Many2one('res.company')
    #currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    pos_category_id = fields.Many2one('pos.category', string="POS Category")
    category_id = fields.Many2one('product.category', string="Category")
    sub_category_id = fields.Many2one('calendar.appointment.type', string="Sub Category")
    qty = fields.Float(string="Qty")
    sub_total = fields.Float( string="Sub Total") #, compute='get_subtotal'
    vat = fields.Float(string="VAT")
    total = fields.Float(string="Total")
    per_revenue_category = fields.Char(string="% of Revenue Category")
    date = fields.Date("Date")
    payment_method = fields.Selection([('cash', 'Cash'), ('net', 'Net Banking'),
                                       ('bank', 'Bank')], string="Payment Method", default='cash')
    location_id = fields.Many2one('res.company', string='Location',default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users')




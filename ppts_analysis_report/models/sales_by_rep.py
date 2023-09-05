from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class SalesByRepSummary(models.Model):
    _name = 'sales.rep.summary'
    _description='SalesByRepSummary'

    name = fields.Char()
    company_id = fields.Many2one('res.company', string='Venue')
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    apt_id = fields.Many2one('appointment.appointment')
    service_id = fields.Many2one('appointment.category')
    pos_id = fields.Many2one('pos.order', compute='get_pos_id')
    sales_rep_id = fields.Many2one('res.users', string='Sales Rep')
    tickets_sold = fields.Integer('Ticket Sold', compute='get_ticket_sold')
    sub_total = fields.Float(string="Sub Total")
    vat = fields.Monetary(currency_field='currency_id', string="VAT")
    total = fields.Float(string="Total")
    date = fields.Date(string="Date")
    product_service = fields.Selection(string='Products/ Services', related="pos_id.lines.product_id.type")

    def get_ticket_sold(self):
        for rec in self:
            apt = self.env['appointment.appointment'].search(
                [('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel']),
                 ('sales_rep_id', '=', rec.sales_rep_id.id)])
            rec.tickets_sold = len(apt)

    def get_pos_id(self):
        for rec in self:
            rec.pos_id = rec.apt_id.pos_order_id.id


class SalesByRepDetail(models.Model):
    _name = 'sales.rep.detail'
    _description="SalesByRepDetail"

    name = fields.Char()
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    apt_id = fields.Many2one('appointment.appointment')
    service_id = fields.Many2one('appointment.category')
    pos_id = fields.Many2one('pos.order')
    sales_rep_id = fields.Many2one('res.users', string='Sales Rep', default=lambda self: self.env.uid)
    sale_date = fields.Date(string='Sale Date', copy=False)
    client = fields.Many2one('res.partner', string="Client")
    item_name = fields.Char(string="Item Name")
    category_id = fields.Many2one('pos.category')
    item_price = fields.Float(string="Item Price")
    quantity = fields.Float(string="Quantity")
    sub_total = fields.Float(string="Sub Total")
    discount = fields.Float(string="Dicount %")
    discount_amount = fields.Float(string="Discount Amount")
    vat = fields.Float(string="VAT")
    total = fields.Float(string="Total")
    date = fields.Date(string="Date")
    product_service = fields.Selection(string='Products/Services', related='pos_id.lines.product_id.type')

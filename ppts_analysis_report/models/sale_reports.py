from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class SalesReportSummary(models.Model):
    _name = 'sales.report.summary'
    _description="SalesReportSummary"

    name = fields.Char()
    sale_date = fields.Date(string='Sale Date', copy=False) #, compute='_get_sale_dates'
    ticket_sold = fields.Integer('Ticket Sold', compute='get_ticket_sold')
    amount_cash = fields.Float('Cash')
    amount_check = fields.Float('Net Banking')
    amount_creditcard = fields.Float('Bank')
    amount_miscellaneous = fields.Float('Miscellaneous')
    amount_total = fields.Float('Total')
    pos_id = fields.Many2one('pos.order')
    apt_id = fields.Many2one('appointment.appointment')
    entered_by = fields.Many2one('res.users', string="Entered by", default=lambda self: self.env.uid)
    sales_rep_id = fields.Many2one('res.users', string="Sales Rep", default=lambda self: self.env.uid)
    location = fields.Many2one('res.company', string="Location",default=lambda self: self.env.company)
    product_service = fields.Selection([
        ('consu', 'Consumable'),('product', 'Product'),
        ('service', 'Service')], string='Product Type')

    def get_ticket_sold(self):
        for rec in self:
            apt = self.env['appointment.appointment'].search(
                [('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel']), ('booking_date', '=', rec.sale_date)])
            rec.ticket_sold = len(rec.pos_id)
            cash = 0.00
            net = 0.00
            bank = 0.00
            credit = 0.00
            pos = self.env['pos.order'].search([('id', '=', rec.pos_id.id)])
            for payment in pos.payment_ids:
                if payment.payment_method_id.name == 'Cash':
                    cash = payment.amount
                if payment.payment_method_id.name == 'Net Banking':
                    net = payment.amount
                if payment.payment_method_id.name == 'Bank':
                    bank = payment.amount
                if payment.payment_method_id.name == 'Apply Credit Balance':
                    bank = payment.amount
            rec.amount_cash = cash
            rec.amount_check = net
            rec.amount_creditcard = bank
            rec.amount_miscellaneous = credit
            rec.amount_total = cash + net + bank + credit



class SalesReportDetail(models.Model):
    _name = 'sales.report.detail'
    _description ="SalesReportDetail"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    apt_id = fields.Many2one('appointment.appointment')
    detail_sale_date = fields.Date(string='Sale Date', copy=False)
    payment_method = fields.Many2many('pos.payment.method', compute='_get_pay_method') #
    client = fields.Many2one('res.partner', string="Client")
    sale_id = fields.Char('Sale')
    item_id = fields.Char(string="Item Name")
    location = fields.Many2one('res.company', string='Location') # , compute='_get_location'
    note = fields.Char(string="Note")
    item_price = fields.Float(string="Item Price")
    quantity = fields.Float(string="Quantity")
    sub_total = fields.Float(string="Sub Total")
    vat = fields.Float(string="VAT")
    discount = fields.Float(string="Dicount %")
    discount_amount = fields.Float(string="Discount Amount")
    item_total = fields.Float(string="Item Total")
    total_paid = fields.Float(string="Total Paid")
    pos_id = fields.Many2one('pos.order')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    entered_by = fields.Many2one('res.users', string="Entered by",default=lambda self: self.env.uid)
    sales_rep_id = fields.Many2one('res.users', string="Sales Rep",default=lambda self: self.env.uid)
    product_service = fields.Selection([
        ('consu', 'Consumable'),('product', 'Product'),
        ('service', 'Service')], string='Product Type')


    def _get_pay_method(self):
        for rec in self:
            apt = self.env['appointment.appointment'].search(
                [('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
            pos = self.env['pos.order'].search([('appt_sale_id', '=', rec.apt_id.id)])
            rec.payment_method = pos.payment_ids.payment_method_id.ids

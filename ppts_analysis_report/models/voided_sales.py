from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class VoidedSalesSummary(models.Model):
    _name = 'voided.sales.summary'
    _description= "VoidedSalesSummary"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    sale_date = fields.Date(string='Sale Date', copy=False)  # , compute='_get_sale_dates'
    ticket_void = fields.Integer('Voided Tickeks', compute='get_ticket_void')
    cash = fields.Monetary(currency_field='currency_id', string="Cash")
    net_bank = fields.Monetary(currency_field='currency_id', string="Net Banking")
    bank = fields.Monetary(currency_field='currency_id', string="Bank")
    others = fields.Monetary(currency_field='currency_id', string="Others")
    total = fields.Monetary(currency_field='currency_id', string="Total")
    total_vat = fields.Monetary(currency_field='currency_id', string="VAT")
    appointment_id = fields.Many2one('appointment.line.id')
    pos_id = fields.Many2one('pos.order')
    apt_id = fields.Many2one('appointment.appointment')

    def get_ticket_void(self):
        for rec in self:
            rec.ticket_void = len(rec.apt_id)
            cash = 0.00
            net = 0.00
            bank = 0.00
            credit = 0.00
            pos = self.env['pos.order'].search([('appt_sale_id', '=', rec.apt_id.id)])
            for payment in pos.payment_ids:
                print(payment.payment_method_id.name)
                if payment.payment_method_id.name == 'Cash':
                    cash = payment.amount
                if payment.payment_method_id.name == 'Net Banking':
                    net = payment.amount
                if payment.payment_method_id.name == 'Bank':
                    bank = payment.amount
                if payment.payment_method_id.name == 'Apply Credit Balance':
                    bank = payment.amount
            rec.cash = cash or 0
            rec.net_bank = net or 0
            rec.bank = bank or 0
            rec.others = credit or 0
            rec.total = cash + net + bank + credit


class VoidedSalesDetail(models.Model):
    _name = 'voided.sales.detail'
    _description ="VoidedSalesDetail"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    date = fields.Date(string='Date', copy=False)
    client = fields.Many2one('res.partner', string="Client")
    sold_by = fields.Many2one('res.users', string='Sold By')
    voided_by = fields.Many2one('res.users', string='Voided By')
    notes = fields.Char(string='Notes')
    color = fields.Char(string='Color')
    size = fields.Integer(string='Size')
    price = fields.Monetary(currency_field='currency_id', string="Price")
    qty = fields.Float('Quantity')
    sub_total = fields.Monetary(currency_field='currency_id',string="Sub Total")
    discount = fields.Float('Disc %')
    vat = fields.Monetary(currency_field='currency_id', string="VAT")
    total = fields.Monetary(currency_field='currency_id', string="Total", compute="_compute_total")
    amt_paid = fields.Monetary(currency_field='currency_id', string="Paid")
    appointment_id = fields.Many2one('appointment.line.id')

    @api.depends('sub_total', 'vat')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.sub_total + rec.vat


    @api.onchange('total')
    def onchange_paid(self):
        appt = self.env['appointment.appointment'].search([('payment_status_apt', '=', 'paid')])
        if appt:
            self.amt_paid = self.total






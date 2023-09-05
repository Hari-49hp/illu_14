from odoo import api, fields, models, _
from datetime import date, timedelta, datetime


class SalesTaxSummary(models.Model):
    _name = 'sales.tax.summary'
    _description ="SalesTaxSummary"

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

    name = fields.Char()
    location_id = fields.Many2one('res.company', string='Location')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True,
                                 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
                                 required=False)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    date = fields.Date(string='Date', copy=False)
    ticket_sold = fields.Integer('Ticket Sold', compute='compute_ticket_sold')
    vat = fields.Monetary(currency_field='currency_id', string="VAT")
    wtax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 2")
    xtax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 3")
    ytax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 4")
    ztax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 5")
    total = fields.Monetary(currency_field='currency_id', string="Total")
    apt_id = fields.Many2one('appointment.appointment')
    pos_id = fields.Many2one('pos.order')
    entered_by = fields.Many2one('res.users', string="Entered By",default=lambda self: self.env.uid)


    def compute_ticket_sold(self):
        for rec in self:
            tickets = self.env['pos.order'].search([('state', '=', 'paid'), ('date_order', '=', rec.date)])
            rec.ticket_sold = len(tickets)





class SalesTaxDetail(models.Model):
    _name = 'sales.tax.detail'
    _description ="SalesTaxDetail"

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
    sale_id = fields.Many2one('pos.order', string='Sale ID')
    log = fields.Char(string='Log')
    item_id = fields.Many2one('product.product', string='Item Name')
    qty = fields.Float(string="Qty")
    vat = fields.Monetary(currency_field='currency_id', string="VAT")
    wtax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 2")
    xtax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 3")
    ytax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 4")
    ztax_rate = fields.Monetary(currency_field='currency_id', string="Tax Rate 5")
    total = fields.Monetary(currency_field='currency_id', string="Total")
    pos_line_id = fields.Many2one('pos.order.line')
    pos_id = fields.Many2one('pos.order')
    entered_by = fields.Many2one('res.users', string="Entered By",default=lambda self: self.env.uid)
